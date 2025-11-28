Welcome to your new dbt project!

### Pre-requisites
- Python version >= 3.11 and < 3.12
- Install the dependencies required using the `requirements.txt` file
- Install the DBT dependencies by running the `dbt deps` command
- Create a `.env` file based on the `.env.local` file and populate the required environment variables based on your local configuration
- Ensure there is data present in the tables targeted by the staging modes for each source

### Using the starter project

Try running the following commands:
- dbt run
- dbt test

### Running as a docker container
To run DBT as a container you have to first build the required pipeline images. The docker files for these are given below:

- [EPC](infrastructure/Dockerfile.epc)  

You can use the following command to run as a docker container:
```sh
docker run -d [-e <environment-variable>...| -env-file <path-to-env-file>] <dbt-image-name> .
```


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
