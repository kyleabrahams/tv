import { Logger, Timer, Storage, Collection } from '@freearhey/core'
import { program } from 'commander'
import { CronJob } from 'cron'
import { QueueCreator, Job, ChannelsParser } from '../../core'
import { Channel } from 'epg-grabber'
import path from 'path'
import { SITES_DIR } from '../../constants'
import axios from 'axios'
import fs from 'fs/promises'
import os from 'os'

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
  continueOnError?: boolean
}

program
  .option('-s, --site <name>', 'Name of the site to parse')
  .option('-c, --channels <path>', 'Path to *.channels.xml file (required if the "--site" attribute is not specified)')
  .option('-o, --output <path>', 'Path to output file', 'guide.xml')
  .option('-l, --lang <code>', 'Filter channels by language (ISO 639-2 code)')
  .option('-t, --timeout <milliseconds>', 'Override the default timeout for each request')
  .option('-d, --delay <milliseconds>', 'Override the default delay between request')
  .option('-x, --proxy <url>', 'Use the specified proxy')
  .option('--days <days>', 'Override the number of days for which the program will be loaded', value => parseInt(value))
  .option('--maxConnections <number>', 'Limit on the number of concurrent requests', value => parseInt(value), 1)
  .option('--cron <expression>', 'Schedule a script run (example: "0 0 * * *")')
  .option('--gzip', 'Create a compressed version of the guide as well', false)
  .option('--continue-on-error', 'Continue when a channel fails', false)
  .parse(process.argv)

const options: GrabOptions = program.opts()

// Fetch XML contents directly from GitHub repository
async function fetchGithubChannels(site: string): Promise<string[]> {
  const apiUrl = `https://api.github.com/repos/iptv-org/epg/contents/sites/${site}`
  const res = await axios.get(apiUrl)
  const files = res.data
    .filter((file: any) => file.name.endsWith('.channels.xml'))
    .map((file: any) => file.download_url)

  const xmlContents: string[] = []
  for (const url of files) {
    const fileRes = await axios.get(url)
    xmlContents.push(fileRes.data)
  }

  return xmlContents
}

async function main() {
  if (!options.site && !options.channels)
    throw new Error('One of the arguments must be presented: `--site` or `--channels`')

  const logger = new Logger()
  logger.start('starting...')
  logger.info('config:')
  logger.tree(options)

  logger.info('loading channels...')
  const storage = new Storage()
  const parser = new ChannelsParser({ storage })

  let files: string[] = []
  if (options.site) {
    // GitHub site XMLs
    files = await fetchGithubChannels(options.site)
  } else if (options.channels) {
    // Local XML files
    files = await storage.list(options.channels)
  }

  // 1️⃣ Fetch & parse channels
  let parsedChannels = new Collection()

  for (const fileOrXml of files) {
    if (options.channels) {
      // Local file path → parse normally
      parsedChannels = parsedChannels.concat(await parser.parse(fileOrXml))
    } else {
      // GitHub XML string → write to temp file, then parse
      const tmpFile = path.join(os.tmpdir(), `tmp-${Date.now()}.xml`)
      await fs.writeFile(tmpFile, fileOrXml)
      parsedChannels = parsedChannels.concat(await parser.parse(tmpFile))
      await fs.unlink(tmpFile) // cleanup
    }
  }

  // 2️⃣ Filter by language if requested
  if (options.lang) {
    parsedChannels = parsedChannels.filter(
      (channel: Channel) => channel.lang === options.lang
    )
  }

  logger.info(`  found ${parsedChannels.count()} channel(s)`)

  // 3️⃣ Run job (supports cron scheduling)
  let runIndex = 1
  async function executeRun() {
    logger.info(`run #${runIndex}:`)
    await runJob({ logger, parsedChannels })
    runIndex++
  }

  if (options.cron) {
    const cronJob = new CronJob(options.cron, executeRun)
    cronJob.start()
  } else {
    await executeRun()
  }
}

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

  try {
    await job.run()
  } catch (error) {
    logger.warn(`⚠️ Job error: ${error instanceof Error ? error.message : error}`)
    if (!options.continueOnError) throw error
    logger.warn('⚠️ Continuing despite job error')
  }

  logger.success(`  done in ${timer.format('HH[h] mm[m] ss[s]')}`)
}

main()