import { Logger, Timer, Storage, Collection } from '@freearhey/core'
import { program } from 'commander'
import { CronJob } from 'cron'
import { QueueCreator, Job, ChannelsParser } from '../../core'
import { Channel } from 'epg-grabber'
import path from 'path'
import fs from 'fs'
import xml2js from 'xml2js'
import { SITES_DIR } from '../../constants'

program
  .option('-s, --site <name>', 'Name of the site to parse')
  .option('-c, --channels <path>', 'Path to *.channels.xml file')
  .option('-o, --output <path>', 'Path to output file', 'guide.xml')
  .option('-d, --dummy-folder <path>', 'Path to folder containing dummy XML files')
  .option('--gzip', 'Create a compressed version of the guide', false)
  .option('--maxConnections <number>', 'Limit on the number of concurrent requests', value => parseInt(value), 1)
  .option('--cron <expression>', 'Schedule a script run')
  .parse(process.argv)

export type GrabOptions = {
  site?: string
  channels?: string
  output: string
  dummyFolder?: string
  gzip: boolean
  maxConnections: number
  cron?: string
}

const options: GrabOptions = program.opts()

async function main() {
  if (!options.site && !options.channels) {
    throw new Error('One of the arguments must be present: `--site` or `--channels`')
  }

  const logger = new Logger()
  logger.start('Starting grab process...')
  logger.tree(options)

  const storage = new Storage()
  const parser = new ChannelsParser({ storage })
  let files: string[] = []

  if (options.site) {
    let pattern = path.join(SITES_DIR, options.site, '*.channels.xml').replace(/\\/g, '/')
    files = await storage.list(pattern)
  } else if (options.channels) {
    files = await storage.list(options.channels)
  }

  let parsedChannels = new Collection()
  for (const filepath of files) {
    parsedChannels = parsedChannels.concat(await parser.parse(filepath))
  }

  if (options.dummyFolder) {
    const dummyFiles = await storage.list(path.join(options.dummyFolder, 'dummy*.xml'))
    if (dummyFiles.length > 0) {
      logger.info(`  Found ${dummyFiles.length} dummy XML file(s) in ${options.dummyFolder}`)
      for (const file of dummyFiles) {
        try {
          const content = fs.readFileSync(file, 'utf-8')
          const parsedData = await xml2js.parseStringPromise(content)
          parsedChannels = parsedChannels.concat(parsedData.tv?.channel || [])
        } catch (error) {
          logger.error(`Failed to parse ${file}: ${error.message}`)
        }
      }
    } else {
      logger.warn(`No dummy XML files found in ${options.dummyFolder}`)
    }
  }

  logger.info(`  Found ${parsedChannels.count()} channels in total`)

  if (options.cron) {
    const cronJob = new CronJob(options.cron, async () => {
      await runJob(logger, parsedChannels)
    })
    cronJob.start()
  } else {
    await runJob(logger, parsedChannels)
  }
}

async function runJob(logger: Logger, parsedChannels: Collection) {
  const timer = new Timer()
  timer.start()

  const queueCreator = new QueueCreator({ parsedChannels, logger, options })
  const queue = await queueCreator.create()
  const job = new Job({ queue, logger, options })

  await job.run()

  const builder = new xml2js.Builder()
  const xmlOutput = builder.buildObject({ tv: { channel: parsedChannels.toArray() } })

  fs.writeFileSync(options.output, xmlOutput, 'utf-8')
  logger.success(`  Guide saved to ${options.output}`)
  logger.success(`  Done in ${timer.format('HH[h] mm[m] ss[s]')}`)
}

main().catch(error => console.error(`Error: ${error.message}`))
