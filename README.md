# Data Request Bot
Chatbot for answering data requests. Upload your database and documentation, and ask it questions about your dataset. Check out the app! http://data-request-bot-lb-179747031.us-east-1.elb.amazonaws.com/
(username and password required, email jshea1820@gmail.com for the credentials)

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

This allows you to specify an application username and password, which will be required when accessing
the web application. It also requires an OpenAI API key, which will be needed to make the LLM calls.

With the configuration variables set, you should be all set to build. Docker is used for the application
build and is a requirement to build and run the application. To build the image, run:

`make build`

This will take a few minutes as your image is built. Once complete, run:

`make run`

This should run the web application. You can access it by opening a browser and navigating to ``http://localhost:8000/``
