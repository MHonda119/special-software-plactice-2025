import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./app.css";
import StartPage from "./pages/StartPage.jsx";
import MenuPage from "./pages/MenuPage.jsx";
import ChatPage from "./pages/ChatPage.jsx";

const router = createBrowserRouter([
  { path: "/", element: <StartPage /> },
  { path: "/menu", element: <MenuPage /> },
  { path: "/chat/:sessionId", element: <ChatPage /> },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
