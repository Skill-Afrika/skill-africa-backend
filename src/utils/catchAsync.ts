// import { RequestHandler } from 'express';
import { Request, Response, NextFunction, RequestHandler } from 'express';

// export interface CustomParamsDictionary {
//   [key: string]: any;
// }

const catchAsync = (fn: RequestHandler) => (req: Request, res: Response, next: NextFunction) => {
  try {
    return Promise.resolve(fn(req, res, next)).catch((err) => next(err));
  } catch (err) {
    next(err);
  }
};

export default catchAsync;
