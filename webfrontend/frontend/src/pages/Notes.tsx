import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from 'react-markdown';

// Sample markdown content for different topics
const notesData: Record<string, Record<string, string>> = {
  biology: {
    anatomy: `# Human Anatomy Notes

## Introduction to Anatomy
Human anatomy is the study of the structure of the human body. It is essential for understanding how our bodies function and how different systems work together.

## Body Systems

### Skeletal System
- **Function**: Provides structural support and protection
- **Components**: 206 bones in adult humans
- **Key Features**:
  - Bone marrow produces blood cells
  - Stores calcium and phosphorus
  - Enables movement through joints

### Muscular System
- **Types of Muscle**:
  1. **Skeletal Muscle**: Voluntary movement
  2. **Cardiac Muscle**: Heart contractions
  3. **Smooth Muscle**: Involuntary organ functions

### Nervous System
- **Central Nervous System (CNS)**:
  - Brain: Control center
  - Spinal cord: Message pathway
- **Peripheral Nervous System (PNS)**:
  - Sensory nerves
  - Motor nerves

## Key Concepts

### Homeostasis
The body's ability to maintain stable internal conditions despite external changes.

### Cell Structure
- **Cell membrane**: Controls what enters/exits
- **Nucleus**: Contains DNA
- **Mitochondria**: Powerhouse of the cell

## Study Tips
1. Use anatomical models and diagrams
2. Practice with labeling exercises
3. Understand function along with structure
4. Connect systems to see the big picture

---

*Continue studying and exploring the fascinating world of human anatomy!*`
  }
};

const Notes = () => {
  const { subjectId, topicId } = useParams();
  const navigate = useNavigate();
  const [showWebView, setShowWebView] = useState(false);

  const subjectName = subjectId === 'biology' ? 'Biology' : subjectId;
  const topicName = topicId === 'anatomy' ? 'Anatomy' : topicId;
  
  const markdownContent = subjectId && topicId ? 
    notesData[subjectId]?.[topicId] || `# ${topicName} Notes\n\nContent coming soon...` :
    "# Notes\n\nNo content available.";

  const handleOpenWebsite = () => {
    setShowWebView(true);
  };

  const handleCloseWebView = () => {
    setShowWebView(false);
  };

  return (
    <div className="pb-20 px-4 pt-6 max-w-lg mx-auto min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button
            size="icon"
            variant="outline"
            onClick={() => navigate(`/subject/${subjectId}`)}
            className="rounded-xl"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold text-gradient">{topicName} Notes</h1>
            <p className="text-sm text-muted-foreground">{subjectName}</p>
          </div>
        </div>
        <Button
          size="sm"
          onClick={handleOpenWebsite}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl flex items-center gap-2"
        >
          <ExternalLink className="w-4 h-4" />
          Open VR
        </Button>
      </div>

      {/* WebXR Fullscreen Modal */}
      {showWebView && (
        <div className="fixed inset-0 z-[999] bg-black flex flex-col items-stretch justify-stretch">
          <div className="absolute top-4 right-4 z-[1000]">
            <Button
              size="sm"
              variant="outline"
              onClick={handleCloseWebView}
              className="rounded-lg bg-white/80 hover:bg-white"
            >
              Close
            </Button>
          </div>
          <iframe
            src="https://my-anatomy-vr-2026.web.app/" // TODO: Replace with your actual WebXR link
            className="w-full h-full border-0"
            title="WebXR Experience"
            allow="xr-spatial-tracking; fullscreen; camera; microphone; autoplay"
            sandbox="allow-scripts allow-same-origin allow-forms allow-modals allow-popups allow-pointer-lock allow-orientation-lock"
          />
        </div>
      )}

      {/* Notes Content */}
      <Card className="p-6 shadow-card">
        <div className="prose prose-sm max-w-none text-foreground markdown-content">
          <ReactMarkdown
            components={{
              h1: ({children}) => <h1 className="text-2xl font-bold mb-4 text-foreground">{children}</h1>,
              h2: ({children}) => <h2 className="text-xl font-semibold mb-3 mt-6 text-foreground">{children}</h2>,
              h3: ({children}) => <h3 className="text-lg font-medium mb-2 mt-4 text-foreground">{children}</h3>,
              p: ({children}) => <p className="mb-3 text-muted-foreground leading-relaxed">{children}</p>,
              ul: ({children}) => <ul className="list-disc ml-6 mb-4">{children}</ul>,
              ol: ({children}) => <ol className="list-decimal ml-6 mb-4">{children}</ol>,
              li: ({children}) => <li className="mb-1 text-muted-foreground">{children}</li>,
              strong: ({children}) => <strong className="font-semibold text-foreground">{children}</strong>,
              em: ({children}) => <em className="italic text-muted-foreground">{children}</em>,
              hr: () => <hr className="my-6 border-border" />,
              blockquote: ({children}) => <blockquote className="border-l-4 border-accent pl-4 italic text-muted-foreground my-4">{children}</blockquote>,
            }}
          >
            {markdownContent}
          </ReactMarkdown>
        </div>
      </Card>

      {/* Study Actions */}
      <Card className="p-4 mt-6 shadow-card gradient-cyber">
        <h3 className="font-semibold text-primary-foreground mb-3">Study Actions</h3>
        <div className="grid grid-cols-2 gap-3">
          <button className="bg-white/10 hover:bg-white/20 backdrop-blur text-primary-foreground rounded-xl p-3 text-sm font-medium transition-all">
            Practice Quiz
          </button>
          <button className="bg-white/10 hover:bg-white/20 backdrop-blur text-primary-foreground rounded-xl p-3 text-sm font-medium transition-all">
            Flashcards
          </button>
        </div>
      </Card>
    </div>
  );
};

export default Notes;