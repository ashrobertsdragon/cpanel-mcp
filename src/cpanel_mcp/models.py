from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

"""Configuration models for cPanel MCP."""


class CpanelAPIConfig(BaseSettings):
    """Configuration for cPanel API connection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    hostname: str = Field(default=...)
    cpanel_username: str = Field(default=...)
    api_token: str = Field(default=...)
    port: int = Field(default=2083)
    ssl: bool = True


class CpanelSSHConfig(BaseSettings):
    """Configuration for cPanel SSH connection."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ssh_key_path: str = Field(default=...)
    ssh_port: int = Field(default=21098)
    server_ip: str = Field(default=...)
    cpanel_username: str = Field(default=...)
