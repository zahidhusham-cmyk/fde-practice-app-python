# Harborline Dispatch — Interview Tasks

You have 45 minutes. You may use your own editor and any AI assistance. We care more about how you work than how many tasks you finish.

The app is an internal dispatch board used by Harborline Freight. Dispatchers already browse shipments, open a shipment, and update its status or assigned driver.

Work in whatever order you like. A strong session usually finishes two or three of these.

## Task 1

Dispatchers have reported they cannot mark a shipment as delivered once it is out for delivery. Please investigate and fix the issue.

## Task 2

Dispatchers want a quicker way to find shipments or to see a snapshot of the board. Add filtering, sorting, or a stats summary to the shipment list. Changes should work end to end.

## Task 3

Dispatchers should be able to book a new shipment from the dashboard. Follow existing patterns, validate input with Pydantic, and add a test.

## Task 4 (stretch)

On a delayed shipment's detail page, add an action that drafts a customer update about the delay. The drafter should be swappable later (for example, for an LLM). A simple implementation is fine for now. Include a test.
