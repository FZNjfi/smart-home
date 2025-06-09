"use client"

import { useState, useEffect } from "react"
import { Send, Mic, Home, Thermometer, Calendar, Clock, Newspaper } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
}

interface NewsItem {
  id: string
  title: string
  summary: string
  category: string
  time: string
}

export default function SmartHomeAssistant() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your smart home assistant. How can I help you today?",
      role: "assistant",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isListening, setIsListening] = useState(false)

  // Mock weather data
  const weatherData = {
    temperature: 72,
    condition: "Sunny",
    humidity: 45,
    location: "Living Room",
  }

  // Mock news data
  const newsItems: NewsItem[] = [
    {
      id: "1",
      title: "Smart Home Technology Advances",
      summary: "New AI-powered home automation systems are becoming more accessible...",
      category: "Technology",
      time: "2 hours ago",
    },
    {
      id: "2",
      title: "Energy Efficiency Tips",
      summary: "Learn how to reduce your home energy consumption with smart devices...",
      category: "Home",
      time: "4 hours ago",
    },
    {
      id: "3",
      title: "Weather Update",
      summary: "Sunny skies expected throughout the week with mild temperatures...",
      category: "Weather",
      time: "6 hours ago",
    },
  ]

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(inputMessage),
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiResponse])
    }, 1000)

    setInputMessage("")
  }

  const generateAIResponse = (input: string): string => {
    const lowerInput = input.toLowerCase()

    if (lowerInput.includes("temperature") || lowerInput.includes("weather")) {
      return `The current temperature is ${weatherData.temperature}°F with ${weatherData.condition.toLowerCase()} conditions. The humidity is at ${weatherData.humidity}%.`
    } else if (lowerInput.includes("time") || lowerInput.includes("clock")) {
      return `The current time is ${currentTime.toLocaleTimeString()}.`
    } else if (lowerInput.includes("date")) {
      return `Today is ${currentTime.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}.`
    } else if (lowerInput.includes("news")) {
      return `Here are the latest news updates: ${newsItems[0].title} - ${newsItems[0].summary}`
    } else if (lowerInput.includes("lights")) {
      return "I can help you control your smart lights. Would you like me to turn them on, off, or adjust the brightness?"
    } else if (lowerInput.includes("music")) {
      return "I can help you play music throughout your home. What would you like to listen to?"
    } else {
      return "I'm here to help with your smart home needs. You can ask me about temperature, time, news, or control your smart devices!"
    }
  }

  const handleVoiceInput = () => {
    setIsListening(!isListening)
    // Voice input functionality would be implemented here
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Header with Date and Time */}
        <div className="lg:col-span-3">
          <Card className="bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Home className="h-8 w-8 text-blue-600" />
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Smart Home Assistant</h1>
                    <p className="text-gray-600">Your intelligent home companion</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-2 text-lg font-semibold">
                    <Clock className="h-5 w-5" />
                    <span>{currentTime.toLocaleTimeString()}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Calendar className="h-4 w-4" />
                    <span>
                      {currentTime.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Weather Widget */}
        <Card className="bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Thermometer className="h-5 w-5 text-orange-500" />
              <span>Climate Control</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600">{weatherData.temperature}°F</div>
                <div className="text-gray-600">{weatherData.condition}</div>
                <div className="text-sm text-gray-500">{weatherData.location}</div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center p-2 bg-blue-50 rounded">
                  <div className="font-semibold">Humidity</div>
                  <div className="text-blue-600">{weatherData.humidity}%</div>
                </div>
                <div className="text-center p-2 bg-green-50 rounded">
                  <div className="font-semibold">Status</div>
                  <div className="text-green-600">Optimal</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* News Section */}
        <Card className="bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Newspaper className="h-5 w-5 text-purple-500" />
              <span>Latest News</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-3">
                {newsItems.map((item) => (
                  <div key={item.id} className="border-b pb-3 last:border-b-0">
                    <div className="flex items-start justify-between mb-1">
                      <Badge variant="secondary" className="text-xs">
                        {item.category}
                      </Badge>
                      <span className="text-xs text-gray-500">{item.time}</span>
                    </div>
                    <h4 className="font-semibold text-sm mb-1">{item.title}</h4>
                    <p className="text-xs text-gray-600 line-clamp-2">{item.summary}</p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* AI Chat Interface */}
        <Card className="bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>AI Assistant</CardTitle>
            <CardDescription>Ask me anything about your smart home</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <ScrollArea className="h-64 pr-4">
              <div className="space-y-3">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            <div className="flex space-x-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me about temperature, time, news, or control devices..."
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                className="flex-1"
              />
              <Button
                onClick={handleVoiceInput}
                variant="outline"
                size="icon"
                className={isListening ? "bg-red-100 text-red-600" : ""}
              >
                <Mic className="h-4 w-4" />
              </Button>
              <Button onClick={handleSendMessage} size="icon">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
