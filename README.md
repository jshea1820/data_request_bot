# Data Request Bot
Chatbot for answering data requests. Connect to your dataset, and have your natural-language data requests answered

## Running locally
Start by cloning the repository.

`git clone https://github.com/jshea1820/data_request_bot.git`

Next, navigate into the working directory.

`cd /path/to/repo/data_request_bot`

Before building, we'll need all environment variables properly set. Start by creating
your ``.env.configure`` file:

`cat .env.configure.example > .env.configure`

`nano .env.configure`

You'll need to set the name of the Docker image that you'll create (``data_request_bot`` works fine). 
If you intend on deploying to ECS, you'll also need to specify the name of your ECS repo.

Next, you'll need to do the same with you application environment variables:

`cat .env.example > .env`

`nano .env`

Here you specify AWS information for connecting to resources, as well as API information for connecting to graph API
and OpenAI APIs.

With the configuration variables set, you should be all set to build. Docker is used for the application
build and is a requirement to build and run the application. To build the image, run:

`make build`

This will take a few minutes as your image is built. Once complete, run:

`make run`

This should run both the web application and the graph API. You can access it by opening a browser and navigating to ``http://localhost:8000/``
