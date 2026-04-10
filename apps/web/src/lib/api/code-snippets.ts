import { apiJson } from '@/lib/api/http';
import type {
  CodeSnippetBundleListEnvelope,
  CodeSnippetBundleResponse,
} from '@/types/studio';

export async function generateCodeSnippets(
  accessToken: string,
  projectId: string,
  runtimeGraphVersion: number | null,
): Promise<CodeSnippetBundleResponse> {
  return apiJson<CodeSnippetBundleResponse>(
    `/api/v1/projects/${projectId}/code-snippets/generate`,
    {
      method: 'POST',
      accessToken,
      body: JSON.stringify({ runtime_graph_version: runtimeGraphVersion }),
    },
  );
}

export async function listCodeSnippetBundles(
  accessToken: string,
  projectId: string,
  limit = 20,
): Promise<CodeSnippetBundleListEnvelope> {
  const q = new URLSearchParams({ limit: String(limit) });
  return apiJson<CodeSnippetBundleListEnvelope>(
    `/api/v1/projects/${projectId}/code-snippets?${q}`,
    { method: 'GET', accessToken },
  );
}

export async function getCodeSnippetBundle(
  accessToken: string,
  projectId: string,
  bundleId: string,
): Promise<CodeSnippetBundleResponse> {
  return apiJson<CodeSnippetBundleResponse>(
    `/api/v1/projects/${projectId}/code-snippets/${bundleId}`,
    { method: 'GET', accessToken },
  );
}
