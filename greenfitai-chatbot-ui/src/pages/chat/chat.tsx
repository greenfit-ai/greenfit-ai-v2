import { useState, useRef } from "react";
import { v4 as uuidv4 } from 'uuid';

import { ChatInput } from "@/components/custom/chatinput";
import { PreviewMessage, ThinkingMessage } from "@/components/custom/message";
import { useScrollToBottom } from '@/components/custom/use-scroll-to-bottom';
import { Overview } from "@/components/custom/overview";
import { Header } from "@/components/custom/header";

interface Message {
  content: {
    text: string;
    chartData?: number[];
  };
  role: "user" | "assistant";
  id: string;
}

// Initialize WebSocket connection
const socket = new WebSocket("ws://localhost:8090");

export function Chat() {
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // Store message handler reference for cleanup
  const messageHandlerRef = useRef<((event: MessageEvent) => void) | null>(null);
  
  // Clean up message handler
  const cleanupMessageHandler = () => {
    if (messageHandlerRef.current && socket) {
      socket.removeEventListener("message", messageHandlerRef.current);
      messageHandlerRef.current = null;
    }
  };

  // Handle message submission
  async function handleSubmit(text?: string) {
    if (!socket || socket.readyState !== WebSocket.OPEN || isLoading) return;
    
    const messageText = text || question;
    const traceId = uuidv4();
    
    // Add user message to chat
    setMessages(prev => [...prev, {
      content: {
        text: messageText
      },
      role: "user",
      id: traceId
    }]);
    
    setIsLoading(true);
    cleanupMessageHandler();
    
    // Send message to WebSocket
    socket.send(messageText);
    setQuestion("");
    
    try {
      const messageHandler = (event: MessageEvent) => {
        setIsLoading(false);
        
        if (event.data.includes("[END]")) {
          cleanupMessageHandler();
          return;
        }
        
        try {
          const parsedData = JSON.parse(event.data);
          
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            
            if (lastMessage?.role === "assistant") {
              // Update existing assistant message
              const updatedMessage: Message = {
                ...lastMessage,
                content: {
                  text: lastMessage.content.text + parsedData.response,
                  chartData: parsedData.data
                }
              };
              return [...prev.slice(0, -1), updatedMessage];
            } else {
              // Create new assistant message
              const newMessage: Message = {
                content: {
                  text: parsedData.response,
                  chartData: parsedData.data
                },
                role: "assistant",
                id: traceId
              };
              return [...prev, newMessage];
            }
          });
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
          
          // Handle non-JSON messages (fallback)
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            
            if (lastMessage?.role === "assistant") {
              const updatedMessage: Message = {
                ...lastMessage,
                content: {
                  text: lastMessage.content.text + event.data,
                  chartData: lastMessage.content.chartData
                }
              };
              return [...prev.slice(0, -1), updatedMessage];
            } else {
              const newMessage: Message = {
                content: {
                  text: event.data
                },
                role: "assistant",
                id: traceId
              };
              return [...prev, newMessage];
            }
          });
        }
      };
      
      messageHandlerRef.current = messageHandler;
      socket.addEventListener("message", messageHandler);
    } catch (error) {
      console.error("WebSocket error:", error);
      setIsLoading(false);
      cleanupMessageHandler();
    }
  }

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-background">
      <Header />
      <div 
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4" 
        ref={messagesContainerRef}
      >
        {messages.length === 0 && <Overview />}
        
        {messages.map((message, index) => (
          <PreviewMessage 
            key={index} 
            message={message} 
          />
        ))}
        
        {isLoading && <ThinkingMessage />}
        
        <div 
          ref={messagesEndRef} 
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>
      
      <div className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <ChatInput
          question={question}
          setQuestion={setQuestion}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}