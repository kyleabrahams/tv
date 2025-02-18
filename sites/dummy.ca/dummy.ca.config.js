const moment = require('moment');
const fs = require('fs');
const xml2js = require('xml2js');
const fetch = require('node-fetch');
const yargs = require('yargs');
const path = require('path');


// Retrieve file paths from command-line arguments using yargs
const argv = yargs(process.argv.slice(2)).options({
  channels: { type: 'string', demandOption: true, description: 'Path to channels file' },
  output: { type: 'string', demandOption: true, description: 'Output file path' },
}).argv;

const channelsFilePath = argv.channels; // channels file path from command line
const outputFilePath = argv.output; // output file path from command line

// Define types for Channel and Program
interface Channel {
  id: string;
  displayName: string;
  site: string;
  lang: string;
  xmltv_id: string;
}

interface Program {
  start: string;
  stop: string;
  channel: string;
  title: string;
  desc: string;
}

// Function to fetch and parse XML data from the provided URL
const fetchXmlData = async (url: string): Promise<any> => {
  try {
    const response = await fetch(url);
    const xmlData = await response.text();

    const parser = new xml2js.Parser();
    const parsedData = await parser.parseStringPromise(xmlData);
    return parsedData;
  } catch (error) {
    console.error("Error fetching or parsing XML data:", error);
    return null; // Return null in case of an error
  }
};

// Parse channels from the input .channels.xml file
const parseChannelsFile = async (channelsFilePath: string): Promise<Channel[]> => {
  try {
    const xmlData = await fs.promises.readFile(channelsFilePath, 'utf-8');
    const parser = new xml2js.Parser();
    const parsedData = await parser.parseStringPromise(xmlData);

    return parsedData.channels.channel.map((channel: any) => ({
      id: channel.site_id[0],
      displayName: channel.display_name[0],
      site: channel.site[0],
      lang: channel.lang[0],
      xmltv_id: channel.xmltv_id[0] || '',
    }));
  } catch (error) {
    console.error(`Error parsing channels file: ${error.message}`);
    return [];
  }
};

// Generate the URL with the current date for fetching the EPG
const generateEpGUrl = (channelId: string): string => {
  const currentDate = moment().format('YYYY-MM-DD-HH-mm-ss'); // Format current date in the required format
  const baseUrl = 'https://raw.githubusercontent.com/kyleabrahams/tv/main/scripts/_epg-end/';
  return `${baseUrl}${channelId}--epg---${currentDate}.xml`; // Construct the full URL
};

// Convert Channels to XML
const generateXmlFromChannels = (channels: Channel[]): string => {
  const builder = new xml2js.Builder();
  const xmlObj = {
    channels: channels.map(channel => ({
      channel: {
        site: channel.site,
        lang: channel.lang,
        xmltv_id: channel.xmltv_id,
        site_id: channel.id,
        display_name: channel.displayName,
      }
    })),
  };
  return builder.buildObject(xmlObj);
};

// Convert Programs to XML
const generateXmlFromPrograms = (programs: Program[]): string => {
  const builder = new xml2js.Builder();
  const xmlObj = {
    programs: programs.map(program => ({
      program: {
        start: program.start,
        stop: program.stop,
        channel: program.channel,
        title: program.title,
        desc: program.desc,
      }
    })),
  };
  return builder.buildObject(xmlObj);
};

// Fetch EPG data for each channel concurrently using Promise.all
const fetchEpGDataForChannels = async (channels: Channel[]): Promise<Program[]> => {
  let programs: Program[] = [];

  const programPromises = channels.map(async (channel) => {
    const epgUrl = generateEpGUrl(channel.id);
    console.log(`Fetching EPG for channel ${channel.displayName} from: ${epgUrl}`);

    try {
      const epgData = await fetchXmlData(epgUrl);

      if (epgData && epgData.programs && epgData.programs.program) {
        const programsData = epgData.programs.program.map((program: any) => ({
          start: program.start[0],
          stop: program.stop[0],
          channel: channel.id,
          title: program.title[0],
          desc: program.desc[0],
        }));

        return programsData;
      } else {
        console.error(`No program data found for ${channel.displayName}`);
        return [];
      }
    } catch (error) {
      console.error(`Error fetching EPG for ${channel.displayName}: ${error.message}`);
      return []; // Return empty array in case of error
    }
  });

  const allPrograms = await Promise.all(programPromises);
  allPrograms.forEach((programList) => programs = programs.concat(programList));

  return programs;
};

// Generate XML Data and save it to a file
const generateXmlData = async () => {
  try {
    // Parse channels from the input file
    const channels = await parseChannelsFile(channelsFilePath);
    if (channels.length === 0) {
      console.error("No channels found. Exiting.");
      return;
    }
    console.log(`Parsed ${channels.length} channels from ${channelsFilePath}`);

    // Fetch EPG data for the channels
    const programs = await fetchEpGDataForChannels(channels);
    console.log(`Fetched ${programs.length} programs for ${channels.length} channels`);

    // Generate XML data for channels and programs
    const channelsXml = generateXmlFromChannels(channels);
    const programsXml = generateXmlFromPrograms(programs);

    // Save the generated XML data to the output file
    fs.writeFileSync(outputFilePath, `${channelsXml}\n${programsXml}`);
    console.log(`Generated and saved channels and programs as XML to ${outputFilePath}`);
  } catch (error) {
    console.error("Error generating XML data:", error);
  }
};

// Execute the function to generate and save XML
generateXmlData();
