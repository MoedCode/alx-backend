#!/usr/bin/env node


import { createClient } from 'redis';

const client = createClient();

let x = new Date()
client.on('error', err => console.log('Redis Client Error', err));

await client.connect();
client.set('key', 'value')
client.set('key1', 'value1')
let res = await  client.get('key')
console.log(1 ,'=>',new Date() - x);
console.log(res);
console.log(2 ,'=>',new Date() - x);

console.log( await client.get('key1'));
await client.hSet('user-session:123', {
    name: 'John',
    surname: 'Smith',
    company: 'Redis',
    age: 29
});
let userSession = await client.hGetAll('user-session:123');
console.log(userSession);