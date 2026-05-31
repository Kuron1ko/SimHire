import { createBrowserRouter, Navigate } from "react-router-dom";

import { EvaluationReportPage } from "./pages/EvaluationReportPage";
import { InterviewRoomPage } from "./pages/InterviewRoomPage";
import { InterviewSetupPage } from "./pages/InterviewSetupPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <InterviewSetupPage />,
  },
  {
    path: "/interview/:sessionId",
    element: <InterviewRoomPage />,
  },
  {
    path: "/reports/:reportId",
    element: <EvaluationReportPage />,
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);
