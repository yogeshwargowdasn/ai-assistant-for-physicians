document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");

  if (fileInput && uploadBtn) {
    fileInput.addEventListener("change", function () {
      const allowed = ["pdf", "doc", "docx", "png"];
      const fileName = fileInput.value.split("\\").pop();
      const ext = fileName ? fileName.split(".").pop().toLowerCase() : "";
      uploadBtn.disabled = !allowed.includes(ext);
    });
  }
});