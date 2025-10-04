import { useEffect, useMemo, useRef, useState } from "react";
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Container,
  Paper,
  Stack,
  TextField,
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  Avatar,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SendIcon from "@mui/icons-material/Send";
import { useNavigate, useParams } from "react-router-dom";
import {
  getMessages as apiGetMessages,
  sendMessage as apiSendMessage,
} from "../services/apiClient.js";

export default function ChatPage() {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [sessionTitle, setSessionTitle] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const listEndRef = useRef(null);

  useEffect(() => {
    // Initial fetch of messages
    (async () => {
      try {
        const ms = await apiGetMessages(sessionId);
        // Map backend fields to UI as needed
        const mapped = ms.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          createdAt: m.created_at || m.createdAt || new Date().toISOString(),
        }));
        setMessages(mapped);
        // Derive title from first user message
        const firstUser = mapped.find((x) => x.role === "user");
        setSessionTitle(
          firstUser ? firstUser.content.slice(0, 20) : "New Chat",
        );
      } catch {
        setMessages([]);
        setSessionTitle("New Chat");
      }
    })();
  }, [sessionId]);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const canSend = useMemo(() => input.trim().length > 0, [input]);

  const handleSend = async () => {
    if (!canSend) return;
    const text = input.trim();
    setInput("");
    try {
      // Optimistic append user message
      const userMsg = {
        id: `temp-${Date.now()}`,
        role: "user",
        content: text,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      const result = await apiSendMessage(sessionId, text);
      // result: { session_uuid, assistant_message: {id, role, content}, usage }
      const assistant = result.assistant_message;
      const assistantMsg = {
        id: assistant.id,
        role: assistant.role,
        content: assistant.content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (!sessionTitle) setSessionTitle(text.slice(0, 20));
    } catch (e) {
      alert(`送信に失敗しました: ${e.message}`);
    }
  };

  return (
    <Box className="chat-shell">
      <AppBar position="static">
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => navigate("/menu")}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" sx={{ ml: 1 }}>
            {sessionTitle || "New Chat"}
          </Typography>
        </Toolbar>
      </AppBar>
      <Container
        maxWidth="md"
        className="chat-content"
        style={{ paddingTop: 16, paddingBottom: 16 }}
      >
        <Paper
          sx={{ width: "100%", display: "flex", flexDirection: "column", p: 2 }}
        >
          <List sx={{ flex: 1, overflowY: "auto" }}>
            {messages.map((m) => (
              <ListItem
                key={m.id}
                alignItems="flex-start"
                sx={{
                  justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <Stack
                  direction={m.role === "user" ? "row-reverse" : "row"}
                  spacing={2}
                  alignItems="flex-start"
                  sx={{ width: "100%" }}
                >
                  <Avatar>{m.role === "user" ? "U" : "A"}</Avatar>
                  <Paper
                    sx={{
                      p: 1.5,
                      maxWidth: "70%",
                      bgcolor: m.role === "user" ? "primary.light" : "grey.100",
                    }}
                  >
                    <ListItemText
                      primary={m.content}
                      secondary={new Date(m.createdAt).toLocaleTimeString()}
                    />
                  </Paper>
                </Stack>
              </ListItem>
            ))}
            <div ref={listEndRef} />
          </List>
          <Stack direction="row" spacing={2}>
            <TextField
              fullWidth
              placeholder="メッセージを入力..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <Button
              variant="contained"
              endIcon={<SendIcon />}
              onClick={handleSend}
              disabled={!canSend}
            >
              送信
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
