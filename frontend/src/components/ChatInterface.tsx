// src/components/ChatInterface.tsx
'use client';
import React, { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

export function ChatInterface() {
  const [query, setQuery] = useState('');
  const handleSend = () => {
    console.log("Send Query:", query);
    // TODO: Call API to send query
    setQuery(''); // Clear input
  };

  return (
    <div className="flex flex-col space-y-2">
       <div className="flex-grow border rounded h-64 overflow-y-auto p-2 bg-muted/30">
         {/* Message history will go here */}
         <p className="text-sm text-muted-foreground">Chat history area...</p>
       </div>
       <Separator />
       <div className="flex items-center space-x-2">
         <Textarea
           placeholder="Ask FaultMaven a question..."
           value={query}
           onChange={(e) => setQuery(e.target.value)}
           rows={2}
           className="flex-grow resize-none"
         />
         <Button onClick={handleSend} disabled={!query.trim()}> {/* Disable if empty */}
           Send
         </Button>
       </div>
    </div>
  );
}
