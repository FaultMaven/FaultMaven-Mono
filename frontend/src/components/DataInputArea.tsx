// src/components/DataInputArea.tsx
'use client';
import React from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function DataInputArea() {
  // TODO: Add state for text input and file handling
  return (
    <Card>
      <CardHeader>
         <CardTitle className="text-lg">Provide Context Data</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
           <Label htmlFor="context-text">Paste Text (Logs, Config, etc.)</Label>
           <Textarea id="context-text" placeholder="Paste relevant text here..." rows={5} />
           <Button size="sm" className="mt-2">Submit Text</Button>
        </div>
        <div className='text-center text-sm text-muted-foreground'>OR</div>
        <div>
           <Label htmlFor="context-file">Upload File</Label>
           <Input id="context-file" type="file" />
           <Button size="sm" className="mt-2">Upload File</Button>
        </div>
      </CardContent>
    </Card>
  );
}
