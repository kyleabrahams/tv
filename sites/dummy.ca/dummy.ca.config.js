import { DummyProvider } from '../../scripts/dummy.js'
const moment = require('moment');

module.exports = {
  site: 'dummy.ca',
  url: 'https://dummyprovider.com',
  channels: [
    { id: 'channel1', name: 'Dummy Channel 1', lang: 'en' },
    { id: 'channel2', name: 'Dummy Channel 2', lang: 'es' }
  ],
  parser: DummyProvider.parser,

  // Generate Channels
  generateChannels() {
    return [
      {
        id: "city-news-247-toronto",
        displayName: "City News 24/7",
      },
      {
        id: "sportsnet-world",
        displayName: "SportsNet World",
      },
    ];
  },

  // Generate Programs for the next 3 days
  generatePrograms() {
    let programs = [];
    let startDate = moment().startOf('day'); // Set start date to the beginning of today
    const daysToGenerate = 3; // Generate programs for the next 3 days

    for (let day = 0; day < daysToGenerate; day++) {
      for (let hour = 0; hour < 24; hour++) {
        // Example for City News 24/7 - You can add more variation here for other channels
        let startTime = startDate.clone().add(day, 'days').add(hour, 'hours');
        let endTime = startTime.clone().add(1, 'hours'); // Assuming 1-hour show duration

        programs.push({
          start: startTime.format('YYYYMMDDHHmmss -0500'),
          stop: endTime.format('YYYYMMDDHHmmss -0500'),
          channel: "city-news-247-toronto",
          title: `City News 24/7 at ${startTime.format('HH:mm')}`,
          desc: `Toronto's breaking news, including the latest updates on weather, traffic, TTC, sports, and stocks.`,
        });

        // Example for SportsNet World - Adding more variety in content
        if (hour % 2 === 0) {  // Alternate the content based on hour for variety
          programs.push({
            start: startTime.format('YYYYMMDDHHmmss -0500'),
            stop: endTime.format('YYYYMMDDHHmmss -0500'),
            channel: "sportsnet-world",
            title: `SportsNet Highlights at ${startTime.format('HH:mm')}`,
            desc: `Catch up on the latest highlights from around the world, including football, hockey, and more.`,
          });
        } else {
          programs.push({
            start: startTime.format('YYYYMMDDHHmmss -0500'),
            stop: endTime.format('YYYYMMDDHHmmss -0500'),
            channel: "sportsnet-world",
            title: `Rugby Super League at ${startTime.format('HH:mm')}`,
            desc: `Watch live coverage of Rugby Super League games, featuring exciting matchups.`,
          });
        }
      }
    }

    // Add logging here to verify that programs are being generated
    console.log('Generated Programs:', programs);
    return programs;
  },
};
