// scripts/list.js
const fs = require('fs');

const directoryPath = './commands/';

fs.readdir(directoryPath, (err, files) => {
  if (err) {
    console.error('Error reading directory:', err.message);
    process.exit(1);
  }
  console.log('Files in directory:', files);
});
