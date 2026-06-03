const fs = require('fs');
const path = require('path');

const logDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
};

const currentLogLevel = logLevels[process.env.LOG_LEVEL || 'info'] || 2;

const formatLog = (level, message, data = null) => {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  return data ? `${logEntry} ${JSON.stringify(data)}` : logEntry;
};

const writeLog = (level, message, data) => {
  const logMessage = formatLog(level, message, data);
  console.log(logMessage);

  if (logLevels[level] <= 0) {
    const errorLog = path.join(logDir, 'error.log');
    fs.appendFileSync(errorLog, logMessage + '\n');
  }
};

module.exports = {
  error: (message, data) => {
    if (logLevels.error <= currentLogLevel) writeLog('error', message, data);
  },
  warn: (message, data) => {
    if (logLevels.warn <= currentLogLevel) writeLog('warn', message, data);
  },
  info: (message, data) => {
    if (logLevels.info <= currentLogLevel) writeLog('info', message, data);
  },
  debug: (message, data) => {
    if (logLevels.debug <= currentLogLevel) writeLog('debug', message, data);
  },
};
