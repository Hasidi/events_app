# Events App


### How to run?

From root directory run: 

`docker compose up tests`

It will run integration tests which calls the rest api service.

### Design

* There is a Flask service, connected to a postgres db and redis.
on every upsert event operation, the service insert the event to a redis queue.
* There is a notification service which responsible for:
  1) Notify for upcoming events (30 min before) - wakeup every minute and checks for upcoming events.
  2) Notify event subscribers for event update/delete operation - connected to a redis queue and looks for subscribers in the db.

* There are two db tables: one for events and one for event subscribers.
Delete does not actually delete the event, rather than mark this row as deleted.
only admin (there is different blueprint for that, and we can use a different authorization) can delete events permanently.
### API

* POST new events
* GET specific event
* GET events - Allow sorting, search event name with a like operation, and filter by event with more than number of participants

* UPDATE specific event
* UPDATE events
* DELETE event
* DELETE events
* POST subscribe to event
* DELETE event admin

  
  For examples see attached postman file or tests.
### Design Notes

* Authentication and Authorization were not implemented. We can use methods like an api-key, or login with a bearer token.
* Async operations can also be used.

### Bonus Features

* Batch operation for create, update, delete.
* Subscribe to event.


![img.png](img.png)