<script lang="ts">
  import { marked } from 'marked';

  let prompt: string = '';
  let chat: string = '';
  let chatHtml: string = '';
  let loading: boolean = false;

  async function sendPrompt(): Promise<void> {
    if (!prompt.trim()) return;
    chat = '';
    chatHtml = '';
    loading = true;

    const res = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, model: 'llama3.2:latest' })
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder('utf-8');

    if (reader) {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        chat += chunk;
        chatHtml = marked(chat); // Convert Markdown to HTML
      }
    }

    loading = false;
  }
</script>


<style>
  textarea {
    width: 100%;
    height: 100px;
    margin-bottom: 10px;
  }
  button {
    padding: 10px 20px;
  }
  #chat {
    margin-top: 20px;
    background: #243434;
    padding: 10px;
    border-radius: 5px;
    white-space: pre-wrap;
  }
  .chat-output {
    text-align: left;
  }
</style>

<h2>Ollama Chat</h2>
<label for="prompt">Enter your prompt:</label><br>
<textarea bind:value={prompt} id="prompt"></textarea><br>
<button on:click={sendPrompt} disabled={loading}>
  {loading ? 'Sending...' : 'Send'}
</button>

<div id="chat">
  {#if loading}
    <p>Loading...</p>
  {:else if chatHtml}
    <div class="chat-output">
      {@html chatHtml}
    </div>
  {:else}
    <p>No response yet.</p>
  {/if}
</div>

