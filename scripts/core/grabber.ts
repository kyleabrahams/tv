import { EPGGrabber, GrabCallbackData, EPGGrabberMock, SiteConfig, Channel } from 'epg-grabber';
import { Logger, Collection } from '@freearhey/core';
import { Queue } from './';
import { GrabOptions } from '../commands/epg/grab';
import { TaskQueue, PromisyClass } from 'cwait';

// Define the required properties for the Grabber class
type GrabberProps = {
  logger: Logger; // Logging utility to track progress or errors
  queue: Queue; // Queue of channels and configurations to process
  options: GrabOptions; // Options to configure grabbing behavior
};

export class Grabber {
  logger: Logger; // Logger instance
  queue: Queue; // Queue instance for processing
  options: GrabOptions; // Configuration options
  grabber: EPGGrabber | EPGGrabberMock; // Grabber instance for fetching data

  constructor({ logger, queue, options }: GrabberProps) {
    this.logger = logger;
    this.queue = queue;
    this.options = options;

    // Define the SiteConfig with all required properties
    const siteConfig: SiteConfig = {
      site: 'xumo.tv', // Name of the site (required)
      url: () => 'http://xumo.tv', // Function to return the base URL
      request: {
        headers: {}, // Custom headers for requests (if needed)
      },
      delay: 1000, // Delay between requests in milliseconds
      parser: (data: any) => data, // Dummy parser function (modify for actual use)
    };

    // Initialize grabber: use a mock during testing, otherwise the actual grabber
    this.grabber =
      process.env.NODE_ENV === 'test'
        ? new EPGGrabberMock(siteConfig)
        : new EPGGrabber(siteConfig);
  }

  // Main grab function to process all channels and return their programs
  async grab(): Promise<{ channels: Collection; programs: Collection }> {
    // Create a task queue to limit concurrent connections
    const taskQueue = new TaskQueue(Promise as PromisyClass, this.options.maxConnections);
    const total = this.queue.size(); // Total number of items in the queue
    const channels = new Collection(); // Collection to store processed channels
    let programs = new Collection(); // Collection to store fetched programs
    let i = 1; // Counter for progress tracking

    // Process all items in the queue concurrently
    await Promise.all(
      this.queue.items().map(
        taskQueue.wrap(
          async (queueItem: { channel: Channel; config: SiteConfig; date: string }) => {
            const { channel, config, date } = queueItem;

            // Add the channel to the collection
            channels.add(channel);

            // Apply timeout option to the request if specified
            if (this.options.timeout !== undefined) {
              const timeout = parseInt(this.options.timeout);
              config.request = { ...config.request, timeout };
            }

            // Apply delay option to the request if specified
            if (this.options.delay !== undefined) {
              const delay = parseInt(this.options.delay);
              config.delay = delay;
            }

            try {
              // Fetch programs for the channel and date using the grabber
              const _programs = await this.grabber.grab(channel, date, config, (data: GrabCallbackData) => {
                const { programs: channelPrograms, date: grabDate } = data;

                // Merge fetched programs into the main collection
                programs = programs.concat(new Collection(channelPrograms));

                // Log successful fetch
                this.logger.info(
                  `  [${i}/${total}] ${channel.site} (${channel.lang}) - ${channel.xmltv_id} - ${grabDate} (${channelPrograms.length} programs)`
                );
              });

              i++; // Increment counter for progress tracking
            } catch (err) {
              // Log error message if the grab fails
              this.logger.error(`Error grabbing data for channel: ${channel.xmltv_id}. Message: ${err.message}`);
            }
          }
        )
      )
    );

    // Return the collections of channels and programs
    return { channels, programs };
  }
}
