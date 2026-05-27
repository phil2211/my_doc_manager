import { useState } from 'react';

export default function UploadDropzone({ onUpload }) {
  const [file, setFile] = useState(null);

  const handleUpload = () => {
    if (file) onUpload(file);
  };

  return (
    <div className="border-2 border-dashed p-8 text-center">
      <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
        Upload PDF
      </button>
    </div>
  );
}