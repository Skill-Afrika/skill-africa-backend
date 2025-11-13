import { PrismaClient } from '@prisma/client';
import config from './config/config';

// add prisma to the NodeJS global type
// interface CustomNodeJsGlobal extends typeof globalThis {
//   prisma: PrismaClient;
// }

// Prevent multiple instances of Prisma Client in development
// declare const global: CustomNodeJsGlobal;
declare global {
  // Augment NodeJS.GlobalThis
  var prisma: PrismaClient | undefined;
}

const prisma = global.prisma || new PrismaClient();

if (config.env === 'development') global.prisma = prisma;

export default prisma;
