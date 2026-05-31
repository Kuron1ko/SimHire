import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type SpeakInput = {
  text: string;
  lang: "zh-CN" | "en-US";
  rate?: number;
  pitch?: number;
  volume?: number;
};

function canUseSpeechSynthesis() {
  return typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
}

export function useSpeechSynthesis() {
  const isSupported = useMemo(canUseSpeechSynthesis, []);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const cancel = useCallback(() => {
    if (!isSupported) {
      return;
    }

    window.speechSynthesis.cancel();
    utteranceRef.current = null;
    setIsSpeaking(false);
  }, [isSupported]);

  const speak = useCallback(
    ({ text, lang, rate = 1, pitch = 1, volume = 1 }: SpeakInput) => {
      if (!isSupported || !text.trim()) {
        return false;
      }

      cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.rate = rate;
      utterance.pitch = pitch;
      utterance.volume = volume;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        utteranceRef.current = null;
        setIsSpeaking(false);
      };
      utterance.onerror = () => {
        utteranceRef.current = null;
        setIsSpeaking(false);
      };

      utteranceRef.current = utterance;
      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
      return true;
    },
    [cancel, isSupported],
  );

  useEffect(() => cancel, [cancel]);

  return {
    isSupported,
    isSpeaking,
    speak,
    cancel,
  };
}
