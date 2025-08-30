import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Loader2, ArrowLeft, BookOpen, MessageSquare, HelpCircle, Bookmark, CheckCircle } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getClassroomData } from '@/services/classroom';

type TabType = 'content' | 'qa' | 'resources' | 'notes';

const ClassroomPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('content');
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  const { data: classroomData, isLoading, error } = useQuery({
    queryKey: ['classroom', id],
    queryFn: () => getClassroomData(id || ''),
    enabled: !!id,
  });

  const handleBack = () => {
    navigate(-1);
  };

  const toggleBookmark = () => {
    // In a real app, this would update the backend
    setIsBookmarked(!isBookmarked);
  };

  const toggleComplete = () => {
    // In a real app, this would update the backend
    setIsCompleted(!isCompleted);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !classroomData) {
    return (
      <div className="container py-8">
        <Button variant="ghost" onClick={handleBack} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold mb-2">Classroom Not Found</h2>
          <p className="text-muted-foreground mb-6">
            The requested classroom could not be found or you don't have access to it.
          </p>
          <Button onClick={handleBack}>Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-6">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="icon" onClick={handleBack} className="mr-2">
          <ArrowLeft className="h-5 w-5" />
          <span className="sr-only">Back</span>
        </Button>
        <div>
          <h1 className="text-2xl font-bold">{classroomData.title}</h1>
          <p className="text-sm text-muted-foreground">
            {classroomData.description}
          </p>
        </div>
        <div className="ml-auto flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={toggleBookmark}>
            <Bookmark className={`h-4 w-4 mr-2 ${isBookmarked ? 'fill-current' : ''}`} />
            {isBookmarked ? 'Bookmarked' : 'Bookmark'}
          </Button>
          <Button size="sm" onClick={toggleComplete}>
            <CheckCircle className="h-4 w-4 mr-2" />
            {isCompleted ? 'Completed' : 'Mark as Complete'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Course Content</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-250px)] pr-4">
                <div className="space-y-2">
                  {classroomData.modules.map((module, index) => (
                    <div key={module.id} className="space-y-1">
                      <div className="px-3 py-2 font-medium text-sm">
                        Module {index + 1}: {module.title}
                      </div>
                      <div className="space-y-1 pl-4">
                        {module.lessons.map((lesson) => (
                          <Button
                            key={lesson.id}
                            variant={lesson.id === id ? 'secondary' : 'ghost'}
                            className={`w-full justify-start text-sm ${lesson.completed ? 'text-green-600' : ''}`}
                            onClick={() => navigate(`/classroom/${lesson.id}`)}
                          >
                            {lesson.completed && (
                              <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                            )}
                            {lesson.title}
                            {lesson.locked && (
                              <span className="ml-auto text-xs text-muted-foreground">
                                Locked
                              </span>
                            )}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabType)}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="content">
                <BookOpen className="h-4 w-4 mr-2" />
                Content
              </TabsTrigger>
              <TabsTrigger value="qa">
                <HelpCircle className="h-4 w-4 mr-2" />
                Q&A
              </TabsTrigger>
              <TabsTrigger value="resources">
                <Bookmark className="h-4 w-4 mr-2" />
                Resources
              </TabsTrigger>
              <TabsTrigger value="notes">
                <MessageSquare className="h-4 w-4 mr-2" />
                Notes
              </TabsTrigger>
            </TabsList>

            <TabsContent value="content" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>{classroomData.currentLesson.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none dark:prose-invert">
                    {classroomData.currentLesson.content}
                  </div>
                  
                  <div className="mt-8 pt-6 border-t flex justify-between">
                    {classroomData.previousLesson && (
                      <Button
                        variant="outline"
                        onClick={() => navigate(`/classroom/${classroomData.previousLesson?.id}`)}
                      >
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Previous: {classroomData.previousLesson.title}
                      </Button>
                    )}
                    <div className="ml-auto">
                      {classroomData.nextLesson ? (
                        <Button
                          onClick={() => navigate(`/classroom/${classroomData.nextLesson?.id}`)}
                        >
                          Next: {classroomData.nextLesson.title}
                          <ArrowLeft className="h-4 w-4 ml-2 transform rotate-180" />
                        </Button>
                      ) : (
                        <Button onClick={toggleComplete}>
                          Complete Module
                          <CheckCircle className="h-4 w-4 ml-2" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="qa" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Questions & Answers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {classroomData.questions.length > 0 ? (
                      classroomData.questions.map((question) => (
                        <div key={question.id} className="border-b pb-4 last:border-0 last:pb-0">
                          <div className="font-medium">{question.text}</div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {question.answer || 'No answer yet'}
                          </div>
                          <div className="text-xs text-muted-foreground mt-2">
                            Asked by {question.askedBy} • {question.timestamp}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No questions yet. Be the first to ask!
                      </div>
                    )}
                    <div className="pt-4">
                      <Button variant="outline" className="w-full">
                        Ask a Question
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="resources" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Additional Resources</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {classroomData.resources.length > 0 ? (
                      <div className="space-y-2">
                        {classroomData.resources.map((resource) => (
                          <a
                            key={resource.id}
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                          >
                            <div className="flex-1">
                              <div className="font-medium">{resource.title}</div>
                              <div className="text-sm text-muted-foreground">{resource.type}</div>
                            </div>
                            <Button variant="ghost" size="sm">
                              View
                            </Button>
                          </a>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No additional resources for this lesson.
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="notes" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>My Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {classroomData.notes ? (
                      <div className="prose max-w-none dark:prose-invert">
                        {classroomData.notes}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No notes yet. Add your personal notes here!
                      </div>
                    )}
                    <div className="pt-4">
                      <Button className="w-full">
                        {classroomData.notes ? 'Edit Notes' : 'Add Notes'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default ClassroomPage;
