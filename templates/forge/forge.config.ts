/**
 * Cloudflare Forge Configuration Template
 * Generates client SDKs, CLIs, and documentation directly from OpenAPI 3.x schema.
 */

export default {
  // Source OpenAPI specification
  spec: "./docs/openapi.yaml",

  // Output targets
  targets: [
    {
      type: "sdk",
      language: "typescript",
      outDir: "./packages/sdk-ts",
      options: {
        packageName: "@maurodruwel/api-client",
      },
    },
    {
      type: "sdk",
      language: "rust",
      outDir: "./crates/api-client-rs",
      options: {
        crateName: "mauro-api-client",
      },
    },
    {
      type: "sdk",
      language: "python",
      outDir: "./packages/sdk-py",
      options: {
        packageName: "mauro_api_client",
      },
    },
    {
      type: "mcp",
      outDir: "./packages/mcp-server",
      options: {
        serverName: "api-mcp-server",
      },
    },
  ],
};
