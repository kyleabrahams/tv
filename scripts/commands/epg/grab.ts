// Logger: Used for logging messages, errors, and structured information during execution.
import { Logger, Timer, Storage, Collection } from '@freearhey/core'  
// Commander: Provides a way to define and parse command-line options.
import { program } from 'commander'  
// CronJob: Allows scheduling of tasks based on cron expressions.
import { CronJob } from 'cron'  
/// Custom modules for processing and managing job queues and parsing channel data:
// QueueCreator: Responsible for creating job queues based on parsed channels.
// Job: Defines and manages individual jobs within the queue.
// ChannelsParser: Parses channel data from provided files.
import { QueueCreator, Job, ChannelsParser } from '../../core'  
// Channel: Represents a single channel from the EPG (Electronic Program Guide) data.
import { Channel } from 'epg-grabber'  
// Path: Provides utilities for handling and transforming file paths.
import path from 'path'  
// SITES_DIR: A constant defining the directory path where site-specific data (e.g., channels) are stored.
import { SITES_DIR } from '../../constants'  


// Define command-line options with Commander
program
  .option('-s, --site <name>', 'Name of the site to parse')
  .option('-c, --channels <path>', 'Path to *.channels.xml file (required if the "--site" attribute is not specified)')
  .option('-o, --output <path>', 'Path to output file', './scripts/xumo.xml')
  .option('-l, --lang <code>', 'Filter channels by language (ISO 639-2 code)')
  .option('-t, --timeout <milliseconds>', 'Override the default timeout for each request')
  .option('-d, --delay <milliseconds>', 'Override the default delay between request')
  .option('--days <days>', 'Override the number of days for which the program will be loaded')
  .option('--maxConnections <number>', 'Limit on the number of concurrent requests', value => parseInt(value), 1)
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
}

const options: GrabOptions = program.opts()

// Main function where the process starts
async function main() {
  // Step 1: Ensure that either site or channels path is provided
  if (!options.site && !options.channels)
    throw new Error('One of the arguments must be presented: `--site` or `--channels`')

  const logger = new Logger()
  logger.start('starting...')
  logger.info('config:')
  logger.tree(options)

  // Step 2: Load the channel files based on provided site or channel path
  logger.info('loading channels...')
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

  // Step 3: Parse the loaded channels into a collection
  let parsedChannels = new Collection()
  for (const filepath of files) {
    parsedChannels = parsedChannels.concat(await parser.parse(filepath))
  }

  // Step 4: Filter channels based on the specified language (if provided)
  if (options.lang) {
    parsedChannels = parsedChannels.filter((channel: Channel) => channel.lang === options.lang)
  }

  logger.info(`  found ${parsedChannels.count()} channel(s)`)

  let runIndex = 1

  // Step 5: Set up a cron job to schedule the job execution every 6 hours
  if (options.cron) {
    const cronJob = new CronJob('0 */6 * * *', async () => {  // Cron expression for every 6 hours
      logger.info(`run #${runIndex}:`)
      await runJob({ logger, parsedChannels })
      runIndex++
    })
    cronJob.start()  // Start the cron job
  } else {
    // Step 6: If no cron job, run the job immediately
    logger.info(`run #${runIndex}:`)
    runJob({ logger, parsedChannels })
  }
}

// Function that runs the job
async function runJob({ logger, parsedChannels }: { logger: Logger; parsedChannels: Collection }) {
  const timer = new Timer()
  timer.start()

  // Step 7: Create a queue based on the parsed channels
  const queueCreator = new QueueCreator({
    parsedChannels,
    logger,
    options
  })
  const queue = await queueCreator.create()

  // Step 8: Create and execute the job
  const job = new Job({
    queue,
    logger,
    options
  })

  await job.run()

  // Log the completion time
  logger.success(`  done in ${timer.format('HH[h] mm[m] ss[s]')}`)
}

// Execute the main function
main()