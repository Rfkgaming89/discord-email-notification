
---

## Email Notifier for Discord

Hey there! Here’s how to get your Email Notifier for Discord up and running.

### 1. Clone the Repository

First, grab the code from GitHub. Open your terminal and run:

```bash
git clone https://github.com/Rfkgaming89/discord-email-notification.git
cd discord-email-notification
```

Switch to the `docker` branch with:

```bash
git checkout docker
```

### 2. Configure the `.env` File

You need to set up your environment variables. Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` to include your IMAP server details, email account, password, Discord token, guild ID, and channel ID.

### 3. Build and Run the Docker Container

Now, let’s build and start the Docker container:

```bash
docker-compose up --build
```

Docker will handle the rest. It may take a moment, so hang tight.

### 4. Verify It’s Working

Check if your container is running:

```bash
docker ps
```

To view logs, use:

```bash
docker-compose logs
```

This will show you any activity or errors. 

### 5. Stop the Container

When you’re done, stop everything with:

```bash
docker-compose down
```

### 6. Updating

If you make changes and need to update, rebuild with:

```bash
docker-compose build
```

Then restart it with:

```bash
docker-compose up
```

Feel free to reach out if you have questions or run into issues. Enjoy the setup!

---
