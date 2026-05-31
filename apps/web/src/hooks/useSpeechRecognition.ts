import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type SpeechRecognitionAlternative = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onend: (() => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventAlternative) => void) | null;
  onresult: ((event: SpeechRecognitionEventAlternative) => void) | null;
  abort: () => void;
  start: () => void;
  stop: () => void;
};

type SpeechRecognitionConstructorAlternative = new () => SpeechRecognitionAlternative;

type SpeechRecognitionEventAlternative = {
  resultIndex: number;
  results: ArrayLike<{
    isFinal: boolean;
    0: {
      transcript: string;
    };
  }>;
};

type SpeechRecognitionErrorEventAlternative = {
  error?: string;
  message?: string;
};

type SpeechWindow = Window &
  typeof globalThis & {
    SpeechRecognition?: SpeechRecognitionConstructorAlternative;
    webkitSpeechRecognition?: SpeechRecognitionConstructorAlternative;
    webkitAudioContext?: typeof AudioContext;
  };

type SpeechRecognitionOptions = {
  language: "zh-CN" | "en-US";
  continuous?: boolean;
};

function getSpeechRecognitionConstructor() {
  if (typeof window === "undefined") {
    return undefined;
  }

  const speechWindow = window as SpeechWindow;
  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
}

function getAudioContextConstructor() {
  if (typeof window === "undefined") {
    return undefined;
  }

  const speechWindow = window as SpeechWindow;
  return speechWindow.AudioContext ?? speechWindow.webkitAudioContext;
}

function joinTranscript(previous: string, next: string) {
  const cleaned = next.trim();
  if (!cleaned) {
    return previous;
  }

  return previous ? `${previous} ${cleaned}` : cleaned;
}

function normalizeVolume(samples: Uint8Array) {
  let sum = 0;

  for (const sample of samples) {
    const normalized = (sample - 128) / 128;
    sum += normalized * normalized;
  }

  const rms = Math.sqrt(sum / samples.length);
  return Math.min(1, rms * 2.5);
}

export function useSpeechRecognition({ language, continuous = true }: SpeechRecognitionOptions) {
  const RecognitionConstructor = useMemo(getSpeechRecognitionConstructor, []);
  const isSupported = Boolean(RecognitionConstructor);
  const [isListening, setIsListening] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognitionAlternative | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const stopAudioMeter = useCallback(() => {
    if (animationFrameRef.current !== null) {
      window.cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    void audioContextRef.current?.close();
    audioContextRef.current = null;
    setVolumeLevel(0);
  }, []);

  const startAudioMeter = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setHasPermission(false);
      setError("当前浏览器不支持麦克风访问，请使用文本输入。");
      return false;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setHasPermission(true);

      const AudioContextConstructor = getAudioContextConstructor();
      if (!AudioContextConstructor) {
        return true;
      }

      const audioContext = new AudioContextConstructor();
      audioContextRef.current = audioContext;

      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 1024;
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      const samples = new Uint8Array(analyser.fftSize);

      const tick = () => {
        analyser.getByteTimeDomainData(samples);
        setVolumeLevel(normalizeVolume(samples));
        animationFrameRef.current = window.requestAnimationFrame(tick);
      };

      tick();
      return true;
    } catch (caught) {
      setHasPermission(false);
      setError(caught instanceof Error ? caught.message : "无法访问麦克风，请使用文本输入。");
      stopAudioMeter();
      return false;
    }
  }, [stopAudioMeter]);

  const stop = useCallback(() => {
    try {
      recognitionRef.current?.stop();
    } catch {
      recognitionRef.current = null;
      stopAudioMeter();
      setIsListening(false);
    }
  }, [stopAudioMeter]);

  const start = useCallback(async () => {
    if (!RecognitionConstructor) {
      setError("当前浏览器不支持语音识别，请使用文本输入。");
      return false;
    }

    if (isListening) {
      return true;
    }

    setError(null);
    const canUseMicrophone = await startAudioMeter();
    if (!canUseMicrophone) {
      return false;
    }

    const recognition = new RecognitionConstructor();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.lang = language;
    recognition.onresult = (event) => {
      let finalText = "";
      let interimText = "";

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const text = result[0]?.transcript ?? "";

        if (result.isFinal) {
          finalText += text;
        } else {
          interimText += text;
        }
      }

      if (finalText) {
        setTranscript((previous) => joinTranscript(previous, finalText));
      }
      setInterimTranscript(interimText.trim());
    };
    recognition.onerror = (event) => {
      setError(event.message || event.error || "语音识别失败，请继续使用文本输入。");
      setHasPermission(event.error === "not-allowed" ? false : hasPermission);
    };
    recognition.onend = () => {
      if (recognitionRef.current === recognition) {
        recognitionRef.current = null;
      }
      setIsListening(false);
      setInterimTranscript((previous) => previous.trim());
      stopAudioMeter();
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
      setIsListening(true);
      return true;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "语音识别启动失败，请使用文本输入。");
      stopAudioMeter();
      setIsListening(false);
      return false;
    }
  }, [RecognitionConstructor, continuous, hasPermission, isListening, language, startAudioMeter, stopAudioMeter]);

  const reset = useCallback(() => {
    setTranscript("");
    setInterimTranscript("");
    setError(null);
    setVolumeLevel(0);
  }, []);

  useEffect(() => {
    return () => {
      try {
        recognitionRef.current?.abort();
      } catch {
        recognitionRef.current = null;
      }
      stopAudioMeter();
    };
  }, [stopAudioMeter]);

  return {
    isSupported,
    isListening,
    hasPermission,
    transcript,
    interimTranscript,
    volumeLevel,
    error,
    start,
    stop,
    reset,
  };
}
