import UploadDropzone from './components/UploadDropzone';

function App() {
  const handleUpload = (file) => {
    console.log("Uploading", file.name);
    // API call to backend would go here
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Document Assistant</h1>
      <UploadDropzone onUpload={handleUpload} />
    </div>
  );
}
export default App;