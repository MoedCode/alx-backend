#!/usr/bin/env node
import Queue from 'bull'; // Correctly import Bull

// Create a Bull queue
const queue = new Queue("queue", {
  redis: { port: 5005, host: '127.0.0.1' } // Fix typos in Redis configuration
});

// Add a job to the queue
queue.add({ title: "job example" });

// Process jobs from the queue
queue.process((job, done) => {
  console.log(`processing job ${job.id}`);
  done();
});

// Listen for job completion
queue.on("completed", (job, result) => {
  console.log(`job completed with result ${result}`);
});

// Listen for job failure
queue.on("failed", (job, err) => {
  console.log(`job failed with error ${err}`);
});
aysha_1