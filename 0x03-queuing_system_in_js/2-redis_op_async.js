#!/usr/bin/env node
// Import required modules
const { createClient } = require('redis');

// Create a Redis client
const client = createClient();

// Event listener for errors
client.on('error', (err) => {
  console.error('Redis client error:', err);
});

// Basic Redis commands
(async () => {
  // Set a key
  await client.set('key', 'value');
  console.log('Set key:', await client.get('key')); // Get the value of the key

  // Use modifiers with SET command
  await client.set('exKey', 'exValue', 'EX', 10, 'NX'); // Set key with expiration and if not exists
  console.log('Set exKey:', await client.get('exKey')); // Get the value of the exKey

  // Use raw Redis commands
  await client.HSET('hashKey', 'field', 'fieldValue'); // Set hash field
  console.log('Hash field value:', await client.HGET('hashKey', 'field')); // Get hash field value
})();

// Transactions (Multi/Exec)
(async () => {
  const multi = client.multi();
  multi.set('transactionKey', 'transactionValue');
  multi.get('transactionKey');
  const [setResult, getResult] = await multi.exec();
  console.log('Transaction result:', setResult, getResult);
})();

// Pub/Sub
(async () => {
  // Subscribe to a channel
  client.subscribe('testChannel');

  // Event listener for messages
  client.on('message', (channel, message) => {
    console.log(`Received message "${message}" on channel "${channel}"`);
  });

  // Publish a message
  client.publish('testChannel', 'Hello from publisher!');
})();

// Lua scripting
(async () => {
  // Define and load a Lua script
  const luaScript = `
    return redis.call('GET', KEYS[1]) + ARGV[1];
  `;
  const scriptResult = await client.eval(luaScript, 1, 'luaKey', 5); // Assuming 'luaKey' exists with value 10
  console.log('Lua script result:', scriptResult); // Should output 15
})();

// Disconnect from Redis
setTimeout(async () => {
  await client.quit(); // Gracefully close connection
  console.log('Disconnected from Redis');
}, 5000); // Disconnect after 5 seconds
