import { Server } from 'http';
import app from './app';
import prisma from './client';
import config from './config/config';
import logger from './config/logger';

let server: Server;
prisma.$connect().then(() => {
  logger.info('Connected to SQL Database');
  server = app.listen(config.port, () => {
    logger.info(`Listening to port ${config.port}`);
  });
});

const exitHandler = () => {
  if (server) {
    server.close(() => {
      logger.info('Server closed');
      process.exit(1);
    });
  } else {
    process.exit(1);
  }
};

const unexpectedErrorHandler = (error: unknown) => {
  logger.error(error);
  exitHandler();
};

// Handle unexpected errors. It is advised to stop the system.
process.on('uncaughtException', unexpectedErrorHandler);
// Handle unhandled promise rejections
process.on('unhandledRejection', unexpectedErrorHandler);

// SIGINT: Manual user termination using CTRL+C
process.on('SIGINT', () => {
  logger.info('SIGINT received');
  if (server) {
    server.close();
  }
});

// SIGTERM: Termination signal from system
process.on('SIGTERM', () => {
  logger.info('SIGTERM received');
  if (server) {
    server.close();
  }
});
