# Evaluation quick start

Please add a section "Evaluation quick start" to your README with the following:

1. **Commit to evaluate:** the branch or tag. We take the last commit before the deadline.
2. **Transport:** stdio or Streamable HTTP. For HTTP, give the port and path (for example `8000`, `/mcp`).
3. **Runtime:** language and version (for example Python 3.12, Node 22), package manager, and any system packages. We run your server in a Linux container on Apple silicon Macs. If you ship a prebuilt image, say whether it is arm64 or amd64.
4. **Setup:** one block of commands, run from the repository root, that installs everything without prompts or manual steps. Say how long it takes and roughly how much disk and memory it needs.
5. **Start command:** the exact command that starts the MCP server.
6. **Prebuilt data:** what is shipped or downloaded, where from, and how big it is. Give the command that rebuilds or refreshes it and how long that takes.
7. **Credentials:** the name of every environment variable your server needs, what each one is for, and whether the server starts without it. Send the values through the organisers' secure channel, never in the repository.
8. **Hosted endpoint (optional):** URL and authentication header. Keep it up until the evaluation is complete.
9. **Declared scope:** your topics, using the topic numbers or names from our topic table, and your geography (cantons as abbreviations such as BE or VD, municipalities by name, or "all of Switzerland"). Name the languages you support.
10. **One example call:** a tool name, its arguments as JSON, and a short description of what it returns. We use it as a first check that your server works.
11. **Known limits:** what is not covered or only partly covered.
12. **robots.txt and terms of use:** the name of the configuration setting and its default.
13. **Parallel use:** whether the server can handle several conversations at the same time, and roughly how long it takes to start.
