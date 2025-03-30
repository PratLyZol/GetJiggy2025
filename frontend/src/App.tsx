import { useState, useEffect } from 'react'
import { CloudArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline'
interface Field {
  name: string;
  description: string;
  required: boolean;
  format: string;
}

interface ProcessedData {
  fields: Field[];
  summary: string;
}

function Button({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-200"
      {...props}
    >
      {children}
    </button>
  );
}

function TextToSpeech() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState("");

  const handleConvertToSpeech = async () => {
    setLoading(true);
    setError(null);
    setAudioUrl("");
    
    try {
      const response = await fetch("http://localhost:8000/api/generate-voice", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate voice");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-[#1C1C1C] flex flex-col items-center justify-start pt-16">
      <h2 className="text-xl font-semibold text-white">Text-to-Speech</h2>
      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : error ? (
        <p className="text-red-400">{error}</p>
      ) : (
        <p className="text-gray-300">{text}</p>
      )}
      <Button onClick={handleConvertToSpeech} disabled={loading}>
        Convert to Speech
      </Button>
      {audioUrl && (
        <audio controls className="mt-4">
          <source src={audioUrl} type="audio/mp3" />
          Your browser does not support the audio element.
        </audio>
      )}
    </div>
  );
}


function App() {
  const [file, setFile] = useState<File | null>(null);
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process file');
      }

      const data = await response.json();
      if (data.data && data.data.fields) {
        setProcessedData(data.data);
      } else {
        throw new Error('Invalid data format received from server');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen bg-[#1C1C1C] flex flex-col items-center justify-start pt-16">
      <div className="w-full px-8 justify-center">
        <h1 className="text-5xl font-light text-white text-center mb-3">
          DocumentProcessor
        </h1>
        <p className="text-base text-gray-400 text-center mb-12">
          Upload any document and get a detailed breakdown of its form fields and requirements.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4 w-full">
  <label className="w-full h-[160px] flex flex-col items-center justify-center border border-dashed border-gray-600 rounded-lg cursor-pointer bg-[#2C2C2C] hover:border-gray-400">
    <CloudArrowUpIcon className="w-8 h-8 text-gray-400 mb-3" />
    <p className="text-sm text-gray-400">Click to upload or drag and drop</p>
    <p className="text-xs text-gray-500 mt-1">PDF, DOCX, CSV, JSON, or TXT</p>
    <input
      type="file"
      className="hidden"
      onChange={handleFileChange}
      accept=".pdf,.docx,.csv,.json,.txt"
    />
  </label>

  {file && (
    <div className="flex items-center gap-2 text-sm text-gray-400">
      <DocumentTextIcon className="w-4 h-4" />
      <span>{file.name}</span>
    </div>
  )}

  <button
    type="submit"
    disabled={!file || loading}
    className="w-full py-2.5 px-4 rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
  >
    {loading ? (
      <div className="flex items-center justify-center">
        <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
      </div>
    ) : (
      'Process File'
    )}
  </button>
</form>

        {error && (
          <div className="mt-4 text-sm text-red-400 flex items-center justify-center gap-2">
            <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}

        {processedData && processedData.fields && (
          <div className="mt-8 text-left">
            <div className="bg-[#2C2C2C] rounded-lg p-4 border border-gray-600 mb-6">
              <h2 className="text-lg font-medium text-white mb-2">Summary</h2>
              <p className="text-gray-300">{processedData.summary}</p>
            </div>
            
            <div>
              <h2 className="text-lg font-medium text-white mb-3">Form Fields</h2>
              <div className="border border-gray-600 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#2C2C2C]">
                    <tr>
                      <th className="py-2 px-4 text-left text-sm font-medium text-gray-300">Field Name</th>
                      <th className="py-2 px-4 text-left text-sm font-medium text-gray-300">Description</th>
                      <th className="py-2 px-4 text-left text-sm font-medium text-gray-300">Required</th>
                      <th className="py-2 px-4 text-left text-sm font-medium text-gray-300">Format</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-600">
                    {processedData.fields.map((field, index) => (
                      <tr key={index} className="bg-[#1C1C1C] hover:bg-[#2C2C2C]">
                        <td className="py-2 px-4 text-sm text-gray-300">{field.name}</td>
                        <td className="py-2 px-4 text-sm text-gray-400">{field.description}</td>
                        <td className="py-2 px-4">
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            field.required 
                              ? 'bg-red-900/20 text-red-400 border border-red-900/30' 
                              : 'bg-green-900/20 text-green-400 border border-green-900/30'
                          }`}>
                            {field.required ? 'Required' : 'Optional'}
                          </span>
                        </td>
                        <td className="py-2 px-4 text-sm text-gray-400">{field.format}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Text-to-Speech Component */}
        <TextToSpeech />
      </div>
    </div>
  )
}

export default App
