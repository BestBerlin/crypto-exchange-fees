FROM python:3.12-slim
LABEL io.modelcontextprotocol.server.name="io.github.BestBerlin/crypto-exchange-fees"
LABEL org.opencontainers.image.source="https://github.com/BestBerlin/crypto-exchange-fees"
LABEL org.opencontainers.image.description="MCP server: official, dated crypto exchange trading fees"
LABEL org.opencontainers.image.licenses="MIT"
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
# stdio MCP server
CMD ["crypto-exchange-fees-mcp"]
