
---

## Email Notifier for Discord

Welcome! Here’s a quick guide to getting your Email Notifier for Discord up and running.

### 1. Clone the Repository

Start by cloning the repository from GitHub. Open your terminal and run:

```bash
git clone https://github.com/Rfkgaming89/discord-email-notification.git
cd discord-email-notification
```

Then switch to the `docker` branch with:

```bash
git checkout docker
```

### 2. Set Up the `.env` File

You’ll need to configure your environment variables. First, copy the example file:

```bash
cp .env.example .env
```

Open `.env` and add your IMAP server details, email credentials, Discord token, guild ID, and channel ID.

### 3. Build and Start the Docker Container

Next, build and launch the Docker container with:

```bash
docker-compose up --build
```

This will take care of setting everything up. It might take a few moments, so please be patient.

### 4. Check Everything’s Running Smoothly

To ensure your container is up and running, use:

```bash
docker ps
```

To view logs and troubleshoot any issues, run:

```bash
docker-compose logs
```

### 5. Stopping the Container

When you’re finished, you can stop the container with:

```bash
docker-compose down
```

### 6. Updating the Setup

If you need to update the setup or make changes, rebuild with:

```bash
docker-compose build
```

Then restart it with:

```bash
docker-compose up
```

### 7. Python Setup Instructions

For details on running the Email Notifier for Discord using Python, please check out the [main GitHub repository](https://github.com/Rfkgaming89/discord-email-notification) and refer to the Python setup section.

Feel free to reach out if you have any questions or run into any issues. Enjoy your setup!

---
