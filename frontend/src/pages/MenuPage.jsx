import { Fragment, useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
// Switch from mock API to backend API
import { getLLMs, createSession, listSessions } from "../services/apiClient.js";

export default function MenuPage() {
  const navigate = useNavigate();
  const [llms, setLlms] = useState([]);
  const [llmId, setLlmId] = useState("");
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const list = await getLLMs();
        setLlms(list.filter((l) => l.is_active !== false));
      } catch {
        setLlms([]);
        // ignore
      }
      try {
        const sess = await listSessions();
        setSessions(sess);
      } catch {
        setSessions([]);
      }
    })();
  }, []);

  const canStart = useMemo(() => Boolean(llmId), [llmId]);

  const handleStart = async () => {
    try {
      const session = await createSession({
        llm: Number(llmId),
        title: "Demo",
      });
      // Backend returns object with uuid. Navigate using uuid.
      const uuid = session.uuid || session.id || session.pk;
      navigate(`/chat/${uuid}`);
    } catch (e) {
      alert(`セッション作成に失敗しました: ${e.message}`);
    }
  };

  return (
    <Container maxWidth="md" className="center-page">
      <Stack spacing={3}>
        <Typography variant="h4">メニュー</Typography>
        <Paper sx={{ p: 2 }}>
          <Stack spacing={2}>
            <Typography variant="h6">LLMモデルの選択</Typography>
            <FormControl fullWidth>
              <InputLabel id="model-select-label">モデル</InputLabel>
              <Select
                labelId="model-select-label"
                label="モデル"
                value={llmId}
                onChange={(e) => setLlmId(e.target.value)}
              >
                {llms.map((m) => {
                  const label = `${m.name} (${m.provider}:${m.model})`;
                  return (
                    <MenuItem key={m.id} value={m.id}>
                      {label}
                    </MenuItem>
                  );
                })}
              </Select>
            </FormControl>
            <Box>
              <Button
                variant="contained"
                onClick={handleStart}
                disabled={!canStart}
              >
                新しいセッションを開始
              </Button>
            </Box>
          </Stack>
        </Paper>

        <Paper sx={{ p: 2 }}>
          <Stack spacing={2}>
            <Typography variant="h6">セッション一覧</Typography>
            <List>
              {sessions.length === 0 && (
                <ListItem>
                  <ListItemText primary="セッションはまだありません" />
                </ListItem>
              )}
              {sessions.map((s, idx) => (
                <Fragment key={s.id}>
                  <ListItem disablePadding>
                    <ListItemButton
                      onClick={() => navigate(`/chat/${s.uuid || s.id}`)}
                    >
                      <ListItemText primary={s.title || s.uuid} />
                    </ListItemButton>
                  </ListItem>
                  {idx < sessions.length - 1 && <Divider component="li" />}
                </Fragment>
              ))}
            </List>
          </Stack>
        </Paper>
      </Stack>
    </Container>
  );
}
