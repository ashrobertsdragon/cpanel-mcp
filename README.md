# cPanel MCP Server

An MCP (Model Context Protocol) server that provides AI assistants with the ability to manage email accounts through cPanel's UAPI. This server enables automated email account creation, deletion, configuration, and forwarding management.

## Features

- **Email Account Management**: Create, delete, and list email accounts
- **Password Management**: Change passwords for existing email accounts
- **Quota Management**: Set and update mailbox storage limits
- **Email Forwarding**: Create, delete, and list email forwarders
- **Client Settings**: Retrieve email client configuration settings
- **Secure Authentication**: Uses cPanel API tokens for secure access

## Available Tools

### Email Account Operations
- `add_email_account(email, password, quota=0)` - Create a new email account
- `delete_email_account(email)` - Delete an existing email account
- `list_email_accounts(domain)` - List all email accounts for a domain
- `change_password(email, new_password)` - Change an email account password
- `update_quota(email, quota)` - Update mailbox size limit
- `get_email_settings(email)` - Get email client configuration settings

### Email Forwarding Operations
- `create_email_forwarder(email, destination)` - Create an email forwarder
- `delete_email_forwarder(email, destination)` - Delete an email forwarder
- `list_email_forwarders(domain)` - List all forwarders for a domain

## Requirements

- Python 3.10 or higher
- cPanel hosting account with API access
- Valid cPanel API token

## Installation

### Using uv (Recommended)

When using uv, no installation is necessary. Instead, you can simply invoke the server directly from Github with the `uvx` command

## Configuration

The server requires the following environment variables:

### Required Variables

- `USERNAME` - Your cPanel username
- `HOSTNAME` - Your cPanel hostname (e.g., `example.com` or `server.example.com`)
- `CPANEL_API_TOKEN` - Your cPanel API token

### Optional Variables

- `PORT` - cPanel port (default: 2083)
- `SSL` - Enable SSL connection (default: true)

## Getting a cPanel API Token

1. Log into your cPanel account
2. Navigate to **Security** → **Manage API Tokens**
3. Click **Create Token**
4. Give it a descriptive name (e.g., "MCP Server")
5. Set appropriate restrictions if needed
6. Copy the generated token

## Usage

### MCP Client Configuration

Add the server to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "cpanel-mcp": {
      "command": "uvx",
      "args": ["cpanel-mcp", "--repository", "https://github.com/ashrobertsdragon/cpanel-mcp"],
      "env": {
        "USERNAME": "your_cpanel_username",
        "HOSTNAME": "your.cpanel.hostname.com",
        "CPANEL_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

## Example Usage

Once connected to an MCP client, you can use natural language commands:

- "Create a new email account support@example.com with password SecurePass123"
- "List all email accounts for example.com"
- "Set up email forwarding from info@example.com to admin@example.com"
- "Change the password for user@example.com to NewPassword456"
- "Delete the email account temp@example.com"
- "Update the quota for sales@example.com to 1000 MB"

## Security Considerations

- **API Token Security**: Never commit your API token to version control
- **Environment Variables**: Use environment variables or secure secret management
- **Network Security**: Ensure your cPanel server supports HTTPS (SSL)
- **Password Policy**: Use strong passwords for email accounts

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API token is correct and active
   - Check that your username matches your cPanel account
   - Ensure the hostname includes the correct domain/subdomain

2. **Connection Issues**
   - Verify the hostname and port are correct
   - Check if SSL is properly configured
   - Ensure your server allows API connections

3. **Permission Errors**
   - Verify your cPanel account has email management permissions
   - Check if the API token has the necessary privileges

## API Reference

The server uses cPanel's UAPI (Unified API) with the following modules:

- **Email Module**: Core email account management
- **Functions Used**:
  - `add_pop` - Create email account
  - `del_pop` - Delete email account  
  - `list_pops` - List email accounts
  - `passwd_pop` - Change password
  - `edit_pop_quota` - Update quota
  - `get_client_settings` - Get email settings
  - `add_forwarder` - Create forwarder
  - `delete_forwarder` - Delete forwarder
  - `list_forwarders` - List forwarders

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review cPanel's UAPI documentation
- Open an issue in the project repository

## Changelog

### v0.1.0

- Initial release
- Basic email account management
- Email forwarding support
- Quota and password management
- MCP integration