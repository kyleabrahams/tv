// Feb 13 958p
import { Logger, Timer, Storage, Collection } from '@freearhey/core'
import { program } from 'commander'
import { CronJob } from 'cron'
import { QueueCreator, Job, ChannelsParser } from '../../core'
import { Channel } from 'epg-grabber'
import path from 'path'
import { execSync } from 'child_process'
import fs from 'fs'
import { SITES_DIR } from '../../constants'

const DUMMY_XML_DIR = '/Users/kyleabrahams/Documents/GitHub/tv/scripts/_epg-end/'

program
  .option('-s, --site <name>', 'Name of the site to parse')
  .option(
    '-c, --channels <path>',
    'Path to *.channels.xml file (required if the "--site" attribute is not specified)'
  )
  .option('-o, --output <path>', 'Path to output file', 'guide.xml')
  .option('-l, --lang <code>', 'Filter channels by language (ISO 639-2 code)')
  .option('-t, --timeout <milliseconds>', 'Override the default timeout for each request')
  .option('-d, --delay <milliseconds>', 'Override the default delay between request')
  .option('-x, --proxy <url>', 'Use the specified proxy')
  .option(
    '--days <days>',
    'Override the number of days for which the program will be loaded (defaults to the value from the site config)',
    value => parseInt(value)
  )
  .option(
    '--maxConnections <number>',
    'Limit on the number of concurrent requests',
    value => parseInt(value),
    1
  )
  .option('--cron <expression>', 'Schedule a script run (example: "0 0 * * *")')
  .option('--gzip', 'Create a compressed version of the guide as well', false)
  .parse(process.argv)

export type GrabOptions = {
  site?: string
  channels?: string
  output: string
  gzip: boolean
  maxConnections: number
  timeout?: string
  delay?: string
  lang?: string
  days?: number
  cron?: string
  proxy?: string
}

const options: GrabOptions = program.opts()

async function main() {
  if (!options.site && !options.channels)
    throw new Error('One of the arguments must be presented: `--site` or `--channels`')

  const logger = new Logger()

  logger.start('Starting XML generation from dummy_epg.py...')

  // Run dummy_epg.py to generate a new XML file
  try {
    execSync('python3 ./scripts/dummy_epg.py', { stdio: 'inherit' })
    logger.success('Dummy EPG XML generated successfully')
  } catch (error) {
    logger.error('Failed to generate dummy XML')
    console.error(error)
    return
  }

  logger.info('Loading channels...')
  const storage = new Storage()
  const parser = new ChannelsParser({ storage })

  let files: string[] = []
  if (options.site) {
    let pattern = path.join(SITES_DIR, options.site, '*.channels.xml')
    pattern = pattern.replace(/\\/g, '/')
    files = await storage.list(pattern)
  } else if (options.channels) {
    files = await storage.list(options.channels)
  }

  let parsedChannels = new Collection()

  // Load and parse existing channels
  for (const filepath of files) {
    parsedChannels = parsedChannels.concat(await parser.parse(filepath))
  }

  // Find the latest dummy XML file
  const latestDummyXml = findLatestDummyXml()
  if (latestDummyXml) {
    logger.info(`Merging dummy XML: ${latestDummyXml}`)
    const dummyChannels = await parser.parse(latestDummyXml)
    parsedChannels = parsedChannels.concat(dummyChannels)
  } else {
    logger.warn('No dummy XML found, proceeding without it...')
  }

  if (options.lang) {
    parsedChannels = parsedChannels.filter((channel: Channel) => channel.lang === options.lang)
  }
  logger.info(`  Found ${parsedChannels.count()} channel(s)`)

  let runIndex = 1
  if (options.cron) {
    const cronJob = new CronJob(options.cron, async () => {
      logger.info(`Run #${runIndex}:`)
      await runJob({ logger, parsedChannels })
      runIndex++
    })
    cronJob.start()
  } else {
    logger.info(`Run #${runIndex}:`)
    await runJob({ logger, parsedChannels })
  }
}

main()

async function runJob({ logger, parsedChannels }: { logger: Logger; parsedChannels: Collection }) {
  const timer = new Timer()
  timer.start()

  const queueCreator = new QueueCreator({
    parsedChannels,
    logger,
    options
  })
  const queue = await queueCreator.create()
  const job = new Job({
    queue,
    logger,
    options
  })

  await job.run()

  logger.success(`  Done in ${timer.format('HH[h] mm[m] ss[s]')}`)
}

/**
 * Finds the latest dummy EPG XML file in the dummy XML directory.
 * @returns {string | null} The path to the latest XML file, or null if none found.
 */
function findLatestDummyXml(): string | null {
  try {
    const files = fs.readdirSync(DUMMY_XML_DIR)
      .filter(file => file.startsWith('dummy--epg') && file.endsWith('.xml'))
      .map(file => ({ file, time: fs.statSync(path.join(DUMMY_XML_DIR, file)).mtime.getTime() }))
      .sort((a, b) => b.time - a.time)

    return files.length > 0 ? path.join(DUMMY_XML_DIR, files[0].file) : null
  } catch (error) {
    console.error('Error finding latest dummy XML:', error)
    return null
  }
}
