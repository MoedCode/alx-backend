0x03-queuing_system_in_js

### Processing Concurrency

By default a call to `queue.process()` will only accept one job at a time for processing. For small tasks like sending emails this is not ideal, so we may specify the maximum active jobs for this type by passing a number:

```js
queue.process('email', 20, function(job, done){
  // ...
});
```

### Pause Processing

Workers can temporarily pause and resume their activity. That is, after calling `pause` they will receive no jobs in their process callback until `resume` is called. The `pause` function gracefully shutdowns this worker, and uses the same internal functionality as the `shutdown` method in [Graceful Shutdown](#graceful-shutdown).

```js
queue.process('email', function(job, ctx, done){
  ctx.pause( 5000, function(err){
    console.log("Worker is paused... ");
    setTimeout( function(){ ctx.resume(); }, 10000 );
  });
});
```

**Note** *The `ctx` parameter from Kue `>=0.9.0` is the second argument of the process callback function and `done` is idiomatically always the last*

**Note** *The `pause` method signature is changed from Kue `>=0.9.0` to move the callback function to the last.*

### Updating Progress

For a "real" example, let's say we need to compile a PDF from numerous slides with [node-canvas](https://github.com/Automattic/node-canvas). Our job may consist of the following data, note that in general you should _not_ store large data in the job it-self, it's better to store references like ids, pulling them in while processing.

```js
queue.create('slideshow pdf', {
    title: user.name + "'s slideshow"
  , slides: [...] // keys to data stored in redis, mongodb, or some other store
});
```

We can access this same arbitrary data within a separate process while processing, via the `job.data` property. In the example we render each slide one-by-one, updating the job's log and progress.

```js
queue.process('slideshow pdf', 5, function(job, done){
  var slides = job.data.slides
    , len = slides.length;

  function next(i) {
    var slide = slides[i]; // pretend we did a query on this slide id ;)
    job.log('rendering %dx%d slide', slide.width, slide.height);
    renderSlide(slide, function(err){
      if (err) return done(err);
      job.progress(i, len, {nextSlide : i == len ? 'itsdone' : i + 1});
      if (i == len) done()
      else next(i + 1);
    });
  }

  next(0);
});
```

### Graceful Shutdown

`Queue#shutdown([timeout,] fn)` signals all workers to stop processing after their current active job is done. Workers will wait `timeout` milliseconds for their active job's done to be called or mark the active job `failed` with shutdown error reason. When all workers tell Kue they are stopped `fn` is called.

```javascript
var queue = require('kue').createQueue();

process.once( 'SIGTERM', function ( sig ) {
  queue.shutdown( 5000, function(err) {
    console.log( 'Kue shutdown: ', err||'' );
    process.exit( 0 );
  });
});
```

**Note** *that `shutdown` method signature is changed from Kue `>=0.9.0` to move the callback function to the last.*

## Error Handling

All errors either in Redis client library or Queue are emitted to the `Queue` object. You should bind to `error` events to prevent uncaught exceptions or debug kue errors.

```javascript
var queue = require('kue').createQueue();

queue.on( 'error', function( err ) {
  console.log( 'Oops... ', err );
});
```

### Prevent from Stuck Active Jobs

Kue marks a job complete/failed when `done` is called by your worker, so you should use proper error handling to prevent uncaught exceptions in your worker's code and node.js process exiting before in handle jobs get done.
This can be achieved in two ways:

1. Wrapping your worker's process function in [Domains](https://nodejs.org/api/domain.html)

  ```js
  queue.process('my-error-prone-task', function(job, done){
    var domain = require('domain').create();
    domain.on('error', function(err){
      done(err);
    });
    domain.run(function(){ // your process function
      throw new Error( 'bad things happen' );
      done();
    });
  });
  ```
 **Notice -** Domains are [deprecated](https://nodejs.org/api/documentation.html#documentation_stability_index) from Nodejs with **stability 0** and it's not recommended to use.

  This is the softest and best solution, however is not built-in with Kue. Please refer to [this discussion](https://github.com/kriskowal/q/issues/120). You can comment on this feature in the related open Kue [issue](https://github.com/Automattic/kue/pull/403).

  You can also use promises to do something like

  ```js
  queue.process('my-error-prone-task', function(job, done){
    Promise.method( function(){ // your process function
      throw new Error( 'bad things happen' );
    })().nodeify(done)
  });
  ```

  but this won't catch exceptions in your async call stack as domains do.



2. Binding to `uncaughtException` and gracefully shutting down the Kue, however this is not a recommended error handling idiom in javascript since you are losing the error context.

  ```js
  process.once( 'uncaughtException', function(err){
    console.error( 'Something bad happened: ', err );
    queue.shutdown( 1000, function(err2){
      console.error( 'Kue shutdown result: ', err2 || 'OK' );
      process.exit( 0 );
    });
  });
  ```

### Unstable Redis connections

Kue currently uses client side job state management and when redis crashes in the middle of that operations, some stuck jobs or index inconsistencies will happen. The consequence is that certain number of jobs will be stuck, and be pulled out by worker only when new jobs are created, if no more new jobs are created, they stuck forever. So we **strongly** suggest that you run watchdog to fix this issue by calling:

```js
queue.watchStuckJobs(interval)
```

`interval` is in milliseconds and defaults to 1000ms

Kue will be refactored to fully atomic job state management from version 1.0 and this will happen by lua scripts and/or BRPOPLPUSH combination. You can read more [here](https://github.com/Automattic/kue/issues/130) and [here](https://github.com/Automattic/kue/issues/38).

## Queue Maintenance

Queue object has two type of methods to tell you about the number of jobs in each state

```js
queue.inactiveCount( function( err, total ) { // others are activeCount, completeCount, failedCount, delayedCount
  if( total > 100000 ) {
    console.log( 'We need some back pressure here' );
  }
});
```

you can also query on an specific job type:

```js
queue.failedCount( 'my-critical-job', function( err, total ) {
  if( total > 10000 ) {
    console.log( 'This is tOoOo bad' );
  }
});
```

and iterating over job ids

```js
queue.inactive( function( err, ids ) { // others are active, complete, failed, delayed
  // you may want to fetch each id to get the Job object out of it...
});
```

however the second one doesn't scale to large deployments, there you can use more specific `Job` static methods:

```js
kue.Job.rangeByState( 'failed', 0, n, 'asc', function( err, jobs ) {
  // you have an array of maximum n Job objects here
});
```
or

```js
kue.Job.rangeByType( 'my-job-type', 'failed', 0, n, 'asc', function( err, jobs ) {
  // you have an array of maximum n Job objects here
});
```

**Note** *that the last two methods are subject to change in later Kue versions.*


### Programmatic Job Management

If you did none of above in [Error Handling](#error-handling) section or your process lost active jobs in any way, you can recover from them when your process is restarted. A blind logic would be to re-queue all stuck jobs:

```js
queue.active( function( err, ids ) {
  ids.forEach( function( id ) {
    kue.Job.get( id, function( err, job ) {
      // Your application should check if job is a stuck one
      job.inactive();
    });
  });
});
```

**Note** *in a clustered deployment your application should be aware not to involve a job that is valid, currently inprocess by other workers.*

### Job Cleanup

Jobs data and search indexes eat up redis memory space, so you will need some job-keeping process in real world deployments. Your first chance is using automatic job removal on completion.

```javascript
queue.create( ... ).removeOnComplete( true ).save()
```

But if you eventually/temporally need completed job data, you can setup an on-demand job removal script like below to remove top `n` completed jobs:

```js
kue.Job.rangeByState( 'complete', 0, n, 'asc', function( err, jobs ) {
  jobs.forEach( function( job ) {
    job.remove( function(){
      console.log( 'removed ', job.id );
    });
  });
});
```

**Note** *that you should provide enough time for `.remove` calls on each job object to complete before your process exits, or job indexes will leak*


## Redis Connection Settings

By default, Kue will connect to Redis using the client default settings (port defaults to `6379`, host defaults to `127.0.0.1`, prefix defaults to `q`). `Queue#createQueue(options)` accepts redis connection options in `options.redis` key.

```javascript
var kue = require('kue');
var q = kue.createQueue({
  prefix: 'q',
  redis: {
    port: 1234,
    host: '10.0.50.20',
    auth: 'password',
    db: 3, // if provided select a non-default redis db
    options: {
      // see https://github.com/mranney/node_redis#rediscreateclient
    }
  }
});
```

`prefix` controls the key names used in Redis.  By default, this is simply `q`. Prefix generally shouldn't be changed unless you need to use one Redis instance for multiple apps. It can also be useful for providing an isolated testbed across your main application.

You can also specify the connection information as a URL string.

```js
var q = kue.createQueue({
  redis: 'redis://example.com:1234?redis_option=value&redis_option=value'
});
```

#### Connecting using Unix Domain Sockets

Since [node_redis](https://github.com/mranney/node_redis) supports Unix Domain Sockets, you can also tell Kue to do so. See [unix-domain-socket](https://github.com/mranney/node_redis#unix-domain-socket) for your redis server configuration.

```javascript
var kue = require('kue');
var q = kue.createQueue({
  prefix: 'q',
  redis: {
    socket: '/data/sockets/redis.sock',
    auth: 'password',
    options: {
      // see https://github.com/mranney/node_redis#rediscreateclient
    }
  }
});
```

#### Replacing Redis Client Module

Any node.js redis client library that conforms (or when adapted) to  [node_redis](https://github.com/mranney/node_redis) API can be injected into Kue. You should only provide a `createClientFactory` function as a redis connection factory instead of providing node_redis connection options.

Below is a sample code to enable [redis-sentinel](https://github.com/ortoo/node-redis-sentinel) to connect to [Redis Sentinel](http://redis.io/topics/sentinel) for automatic master/slave failover.

```javascript
var kue = require('kue');
var Sentinel = require('redis-sentinel');
var endpoints = [
  {host: '192.168.1.10', port: 6379},
  {host: '192.168.1.11', port: 6379}
];
var opts = options || {}; // Standard node_redis client options
var masterName = 'mymaster';
var sentinel = Sentinel.Sentinel(endpoints);

var q = kue.createQueue({
   redis: {
      createClientFactory: function(){
         return sentinel.createClient(masterName, opts);
      }
   }
});
```

**Note** *that all `<0.8.x` client codes should be refactored to pass redis options to `Queue#createQueue` instead of monkey patched style overriding of `redis#createClient` or they will be broken from Kue `0.8.x`.*

#### Using ioredis client with cluster support

```javascript

var Redis = require('ioredis');
var kue = require('kue');

// using https://github.com/72squared/vagrant-redis-cluster

var queue = kue.createQueue({
    redis: {
      createClientFactory: function () {
        return new Redis.Cluster([{
          port: 7000
        }, {
          port: 7001
        }]);
      }
    }
  });
```

## User-Interface

The UI is a small [Express](https://github.com/strongloop/express) application.
A script is provided in `bin/` for running the interface as a standalone application
with default settings. You may pass in options for the port, redis-url, and prefix. For example:

```
node_modules/kue/bin/kue-dashboard -p 3050 -r redis://127.0.0.1:3000 -q prefix
```

You can fire it up from within another application too:


```js
var kue = require('kue');
kue.createQueue(...);
kue.app.listen(3000);
```

The title defaults to "Kue", to alter this invoke:

```js
kue.app.set('title', 'My Application');
```

**Note** *that if you are using non-default Kue options, `kue.createQueue(...)` must be called before accessing `kue.app`.*

### Third-party interfaces

You can also use [Kue-UI](https://github.com/StreetHub/kue-ui) web interface contributed by [Arnaud Bénard](https://github.com/arnaudbenard)


## JSON API

Along with the UI Kue also exposes a JSON API, which is utilized by the UI.

### GET /job/search?q=

Query jobs, for example "GET /job/search?q=avi video":

```js
["5", "7", "10"]
```

By default kue indexes the whole Job data object for searching, but this can be customized via calling `Job#searchKeys` to tell kue which keys on Job data to create index for:

```javascript
var kue = require('kue');
queue = kue.createQueue();
queue.create('email', {
    title: 'welcome email for tj'
  , to: 'tj@learnboost.com'
  , template: 'welcome-email'
}).searchKeys( ['to', 'title'] ).save();
```

Search feature is turned off by default from Kue `>=0.9.0`. Read more about this [here](https://github.com/Automattic/kue/issues/412). You should enable search indexes and add [reds](https://www.npmjs.com/package/reds) in your dependencies if you need to:

```javascript
var kue = require('kue');
q = kue.createQueue({
    disableSearch: false
});
```

```
npm install reds --save
```

### GET /stats

Currently responds with state counts, and worker activity time in milliseconds:

```js
{"inactiveCount":4,"completeCount":69,"activeCount":2,"failedCount":0,"workTime":20892}
```

### GET /job/:id

Get a job by `:id`:

```js
{"id":"3","type":"email","data":{"title":"welcome email for tj","to":"tj@learnboost.com","template":"welcome-email"},"priority":-10,"progress":"100","state":"complete","attempts":null,"created_at":"1309973155248","updated_at":"1309973155248","duration":"15002"}
```

### GET /job/:id/log

Get job `:id`'s log:

```js
['foo', 'bar', 'baz']
```

### GET /jobs/:from..:to/:order?

Get jobs with the specified range `:from` to `:to`, for example "/jobs/0..2", where `:order` may be "asc" or "desc":

```js
[{"id":"12","type":"email","data":{"title":"welcome email for tj","to":"tj@learnboost.com","template":"welcome-email"},"priority":-10,"progress":0,"state":"active","attempts":null,"created_at":"1309973299293","updated_at":"1309973299293"},{"id":"130","type":"email","data":{"title":"welcome email for tj","to":"tj@learnboost.com","template":"welcome-email"},"priority":-10,"progress":0,"state":"active","attempts":null,"created_at":"1309975157291","updated_at":"1309975157291"}]
```

### GET /jobs/:state/:from..:to/:order?

Same as above, restricting by `:state` which is one of:

    - active
    - inactive
    - failed
    - complete

### GET /jobs/:type/:state/:from..:to/:order?

Same as above, however restricted to `:type` and `:state`.

### DELETE /job/:id

Delete job `:id`:

    $ curl -X DELETE http://local:3000/job/2
    {"message":"job 2 removed"}

### POST /job

Create a job:

    $ curl -H "Content-Type: application/json" -X POST -d \
        '{
           "type": "email",
           "data": {
             "title": "welcome email for tj",
             "to": "tj@learnboost.com",
             "template": "welcome-email"
           },
           "options" : {
             "attempts": 5,
             "priority": "high"
           }
         }' http://localhost:3000/job
    {"message": "job created", "id": 3}

You can create multiple jobs at once by passing an array. In this case, the response will be an array too, preserving the order:

    $ curl -H "Content-Type: application/json" -X POST -d \
        '[{
           "type": "email",
           "data": {
             "title": "welcome email for tj",
             "to": "tj@learnboost.com",
             "template": "welcome-email"
           },
           "options" : {
             "attempts": 5,
             "priority": "high"
           }
         },
         {
           "type": "email",
           "data": {
             "title": "followup email for tj",
             "to": "tj@learnboost.com",
             "template": "followup-email"
           },
           "options" : {
             "delay": 86400,
             "attempts": 5,
             "priority": "high"
           }
         }]' http://localhost:3000/job
    [
      {"message": "job created", "id": 4},
      {"message": "job created", "id": 5}
    ]

Note: when inserting multiple jobs in bulk, if one insertion fails Kue will keep processing the remaining jobs in order. The response array will contain the ids of the jobs added successfully, and any failed element will be an object describing the error: `{"error": "error reason"}`.


## Parallel Processing With Cluster

The example below shows how you may use [Cluster](http://nodejs.org/api/cluster.html) to spread the job processing load across CPUs. Please see [Cluster module's documentation](http://nodejs.org/api/cluster.html) for more detailed examples on using it.

When cluster `.isMaster` the file is being executed in context of the master process, in which case you may perform tasks that you only want once, such as starting the web app bundled with Kue. The logic in the `else` block is executed _per worker_.

```js
var kue = require('kue')
  , cluster = require('cluster')
  , queue = kue.createQueue();

var clusterWorkerSize = require('os').cpus().length;

if (cluster.isMaster) {
  kue.app.listen(3000);
  for (var i = 0; i < clusterWorkerSize; i++) {
    cluster.fork();
  }
} else {
  queue.process('email', 10, function(job, done){
    var pending = 5
      , total = pending;

    var interval = setInterval(function(){
      job.log('sending!');
      job.progress(total - pending, total);
      --pending || done();
      pending || clearInterval(interval);
    }, 1000);
  });
}
```

This will create an `email` job processor (worker) per each of your machine CPU cores, with each you can handle 10 concurrent email jobs, leading to total `10 * N` concurrent email jobs processed in your `N` core machine.

Now when you visit Kue's UI in the browser you'll see that jobs are being processed roughly `N` times faster! (if you have `N` cores).

## Securing Kue

Through the use of app mounting you may customize the web application, enabling TLS, or adding additional middleware like `basic-auth-connect`.

```bash
$ npm install --save basic-auth-connect
```

```js
var basicAuth = require('basic-auth-connect');
var app = express.createServer({ ... tls options ... });
app.use(basicAuth('foo', 'bar'));
app.use(kue.app);
app.listen(3000);
```

## Testing

Enable test mode to push all jobs into a `jobs` array. Make assertions against
the jobs in that array to ensure code under test is correctly enqueuing jobs.

```js
queue = require('kue').createQueue();

before(function() {
  queue.testMode.enter();
});

afterEach(function() {
  queue.testMode.clear();
});

after(function() {
  queue.testMode.exit()
});

it('does something cool', function() {
  queue.createJob('myJob', { foo: 'bar' }).save();
  queue.createJob('anotherJob', { baz: 'bip' }).save();
  expect(queue.testMode.jobs.length).to.equal(2);
  expect(queue.testMode.jobs[0].type).to.equal('myJob');
  expect(queue.testMode.jobs[0].data).to.eql({ foo: 'bar' });
});
```

**IMPORTANT:** By default jobs aren't processed when created during test mode. You can enable job processing by passing true to testMode.enter

```js
before(function() {
  queue.testMode.enter(true);
});
```


## Screencasts

  - [Introduction](http://www.screenr.com/oyNs) to Kue
  - API [walkthrough](https://vimeo.com/26963384) to Kue

## Contributing

**We love contributions!**

When contributing, follow the simple rules:

* Don't violate [DRY](http://programmer.97things.oreilly.com/wiki/index.php/Don%27t_Repeat_Yourself) principles.
* [Boy Scout Rule](http://programmer.97things.oreilly.com/wiki/index.php/The_Boy_Scout_Rule) needs to have been applied.
* Your code should look like all the other code – this project should look like it was written by one person, always.
* If you want to propose something – just create an issue and describe your question with as much description as you can.
* If you think you have some general improvement, consider creating a pull request with it.
* If you add new code, it should be covered by tests. No tests – no code.
* If you add a new feature, don't forget to update the documentation for it.
* If you find a bug (or at least you think it is a bug), create an issue with the library version and test case that we can run and see what are you talking about, or at least full steps by which we can reproduce it.

## License

(The MIT License)

Copyright (c) 2011 LearnBoost &lt;tj@learnboost.com&gt;

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.