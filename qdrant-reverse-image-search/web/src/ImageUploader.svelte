<script>
  let uploadedImages = [];
  let loading = false;

  async function handleFileChange(event) {
    const files = event.target.files;
    await processFiles(files);
  }

  async function handleDrop(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    await processFiles(files);
  }

  async function processFiles(files) {
    loading = true;
    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch("http://localhost:8000/upload-image/", {
          method: "POST",
          body: formData
        });

        if (!res.ok) throw new Error("Upload failed");
        uploadedImages = []; // Clear previous images
        const data = await res.json();
        uploadedImages = [...uploadedImages, data];
        //uploadedImages = data[0];
        console.log("Uploaded image data:", uploadedImages);
      } catch (err) {
        console.error("Error uploading image:", err);
      }
    }
    loading = false;
  }

  function triggerFileInput() {
    document.getElementById("imageUpload").click();
  }
</script>

<style>
  .drop-zone {
    border: 2px dashed #6c757d;
    border-radius: 8px;
    padding: 40px;
    text-align: center;
    color: #6c757d;
    background-color: #f8f9fa;
    transition: background-color 0.3s ease;
    cursor: pointer;
  }

  .masonry {
  column-count: 4;
  column-gap: 1rem;
}

.masonry .card {
  display: inline-block;
  width: 100%;
  margin-bottom: 1rem;
  break-inside: avoid;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
}

.card-img-top {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
}

.card-body {
  padding: 0.75rem;
}

@media (max-width: 1200px) {
  .masonry { column-count: 3; }
}

@media (max-width: 768px) {
  .masonry { column-count: 2; }
}

@media (max-width: 576px) {
  .masonry { column-count: 1; }
}
</style>

<div class="container py-4">
  <!-- Upload Section -->
  <div class="card mb-4">
    <div class="card-body">
      <h5 class="card-title">Upload an Image</h5>
      <div
        class="drop-zone"
        on:click={triggerFileInput}
        on:dragover|preventDefault
        on:drop={handleDrop}
      >
        <p>Drag & drop your image here, or click to select</p>
        <input type="file" id="imageUpload" accept="image/*" hidden on:change={handleFileChange} />
      </div>
    </div>
  </div>

   {#if loading}
  <div class="text-center my-3">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
{/if} 

  <!-- Gallery Section -->
  <div class="masonry">
    {#each uploadedImages as data}
    {#each data as img}
    <div class="card">
        <img src='./{img.payload.path}' class="card-img-top" alt={img.payload.path} />
        <div class="card-body">
          <h6 class="card-title">{img.id}</h6>
          <p class="card-text">Score: {img.score}</p>
        </div>
      </div>
      {/each}
    {/each}
  </div>
</div>
