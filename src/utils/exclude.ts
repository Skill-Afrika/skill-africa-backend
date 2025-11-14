/**
 * Exclude keys from object
 * @param obj
 * @param keys
 * @returns
 */
const exclude = <Type, Key extends keyof Type>(obj: Type, keys: Key[]): Omit<Type, Key> => {
  // Return a shallow copy with the specified keys omitted.
  // Avoid mutating the original object in case it's frozen or referenced elsewhere.
  const result = { ...(obj as any) } as any;
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(result, key)) {
      delete result[key];
    }
  }
  return result as Omit<Type, Key>;
};

export default exclude;
