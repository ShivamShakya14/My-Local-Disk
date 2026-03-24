document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop_zone');
  const fileInput = document.getElementById('file_input');
  const folderForm = document.getElementById('folder_form');
  const currentPath = window.location.pathname.substring(1);
  const downloadBtn = document.getElementById("download_btn");
  const deleteBtn = document.getElementById("delete_btn");
  const renameBtn = document.getElementById("rename_btn");

  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
  });
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
  });
  fileInput.addEventListener('change', () => {
    handleFiles(fileInput.files);
  });

  function handleFiles(files) {
    if (files.length === 0) return;
    const formData = new FormData();
    for (const file of files) {
      formData.append('file', file);
    }

    fetch(`/upload?path=${encodeURIComponent(currentPath)}`, {
      method: 'POST',
      body: formData
    }).then(resp => resp.json())
      .then(data => {
        alert("Uploaded: " + data.uploaded.join(', '));
        location.reload();
      });
  }

  folderForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const folderName = document.getElementById('new_folder').value.trim();
    if (!folderName) return;

    const formData = new FormData();
    formData.append('foldername', folderName);

    fetch(`/mkdir?path=${encodeURIComponent(currentPath)}`, {
      method: 'POST',
      body: formData
    }).then(res => res.json())
      .then(data => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('newFolderModal'));
        modal.hide();
        alert('Folder created');
        location.reload();
      });
  });

  function updateButtons() {
    const selected = [...document.querySelectorAll(".select_item:checked")];
    const selectedCount = selected.length;
    renameBtn.disabled = selectedCount !== 1;
    downloadBtn.disabled = selectedCount === 0;
    deleteBtn.disabled = selectedCount === 0;
  }

  document.addEventListener('change', (e) => {
    if (e.target.classList.contains('select_item')) {
      updateButtons();
    }
  });

  updateButtons(); // initial

  downloadBtn.onclick = () => {
    const selected = [...document.querySelectorAll(".select_item:checked")].map(cb => cb.dataset.name);
    if (selected.length === 0) return;

    if (selected.length === 1) {
      const isDir = document.querySelector(".select_item:checked").dataset.isdir === 'true';
      if (!isDir) {
        window.location.href = `/download/${encodeURIComponent(selected[0])}`;
        return;
      }
    }

    fetch(`/download_batch?path=${encodeURIComponent(currentPath)}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({items: selected})
    }).then(resp => resp.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'download.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }).catch(err => alert(err));
  };

  deleteBtn.onclick = () => {
    if (!confirm("Are you sure you want to delete selected items?")) return;
    const selected = [...document.querySelectorAll(".select_item:checked")].map(cb => cb.dataset.name);
    const formData = new FormData();
    selected.forEach(name => formData.append("names[]", name));

    fetch(`/delete?path=${encodeURIComponent(currentPath)}`, {
      method: "POST",
      body: formData
    }).then(res => res.json())
      .then(data => {
        if (data.status === "deleted") {
          alert(`Deleted: ${data.deleted.join(', ')}`);
          location.reload();
        } else {
          alert("Error: " + (data.error || "Unknown error"));
        }
      });
  };

  renameBtn.onclick = () => {
    const selected = [...document.querySelectorAll(".select_item:checked")];
    if (selected.length !== 1) return;

    const oldName = selected[0].dataset.name;
    const newName = prompt("Enter new name:", oldName);
    if (!newName || newName.trim() === "" || newName === oldName) return;

    const formData = new FormData();
    formData.append("old_name", oldName);
    formData.append("new_name", newName.trim());

    fetch(`/rename?path=${encodeURIComponent(currentPath)}`, {
      method: "POST",
      body: formData
    }).then(res => res.json())
      .then(data => {
        if (data.status === "renamed") {
          alert(`Renamed to: ${data.new_name}`);
          location.reload();
        } else {
          alert("Error: " + (data.error || "Unknown error"));
        }
      });
  };

  // Dark Mode Toggle
  document.getElementById('toggle_dark').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
  });
});
