import { useEffect, useMemo, useRef, useState } from "react";

import { normalizedToPixels } from "./lib/bbox";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

type ClassItem = {
  id: number;
  name: string;
};

type ImageItem = {
  id: string;
  filename: string;
};

type LabelItem = {
  class_id: number;
  class_name: string;
  bbox: {
    cx: number;
    cy: number;
    width: number;
    height: number;
  };
  confidence?: number | null;
};

type BoxOverlay = {
  id: string;
  className: string;
  color: string;
  style: {
    left: number;
    top: number;
    width: number;
    height: number;
    borderColor: string;
    color: string;
  };
  confidence?: string;
};

const PALETTE = [
  "#38bdf8",
  "#f97316",
  "#a855f7",
  "#facc15",
  "#22c55e",
  "#ef4444",
  "#0ea5e9",
  "#ec4899",
  "#8b5cf6",
  "#f87171"
];

const pickColor = (classId: number) => PALETTE[classId % PALETTE.length];

function formatConfidence(confidence?: number | null) {
  if (confidence === undefined || confidence === null) {
    return undefined;
  }
  if (confidence <= 1) {
    return `${(confidence * 100).toFixed(1)}%`;
  }
  return confidence.toFixed(2);
}

function App() {
  const [classes, setClasses] = useState<ClassItem[]>([]);
  const [images, setImages] = useState<ImageItem[]>([]);
  const [selectedImage, setSelectedImage] = useState<string>("");
  const [labels, setLabels] = useState<LabelItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const [imageDimensions, setImageDimensions] = useState<{ width: number; height: number } | null>(
    null
  );

  const imageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    const fetchInitial = async () => {
      try {
        const [classRes, imageRes] = await Promise.all([
          fetch(`${API_BASE}/classes`),
          fetch(`${API_BASE}/images`)
        ]);

        if (!classRes.ok) {
          throw new Error(`加载类别失败：${classRes.statusText}`);
        }
        if (!imageRes.ok) {
          throw new Error(`加载图片列表失败：${imageRes.statusText}`);
        }

        const classData: ClassItem[] = await classRes.json();
        const imageData: ImageItem[] = await imageRes.json();
        setClasses(classData);
        setImages(imageData);
        if (imageData.length > 0) {
          setSelectedImage((current) => current || imageData[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "初始化失败");
      }
    };

    fetchInitial();
  }, []);

  useEffect(() => {
    if (!selectedImage) {
      setLabels([]);
      return;
    }

    const controller = new AbortController();

    const fetchLabels = async () => {
      setLoading(true);
      setImageError(null);
      try {
        const response = await fetch(`${API_BASE}/label/${selectedImage}`, {
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`加载标注失败：${response.statusText}`);
        }
        const data: LabelItem[] = await response.json();
        setLabels(data);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setLabels([]);
        setError(err instanceof Error ? err.message : "加载标注失败");
      } finally {
        setLoading(false);
      }
    };

    fetchLabels();

    return () => controller.abort();
  }, [selectedImage]);

  useEffect(() => {
    const updateDimensions = () => {
      const el = imageRef.current;
      if (!el) return;
      setImageDimensions({ width: el.clientWidth, height: el.clientHeight });
    };

    window.addEventListener("resize", updateDimensions);
    updateDimensions();
    return () => window.removeEventListener("resize", updateDimensions);
  }, [selectedImage, labels.length]);

  const overlays = useMemo<BoxOverlay[]>(() => {
    if (!imageDimensions) {
      return [];
    }
    return labels.map((label, index) => {
      const { left, top, width, height } = normalizedToPixels(label.bbox, imageDimensions);
      const color = pickColor(label.class_id);

      return {
        id: `${label.class_id}-${index}`,
        className: label.class_name,
        color,
        style: {
          left,
          top,
          width,
          height,
          borderColor: color,
          color
        },
        confidence: formatConfidence(label.confidence ?? undefined)
      };
    });
  }, [imageDimensions, labels]);

  const imageSrc = selectedImage ? `${API_BASE}/image/${selectedImage}` : "";

  const legend = useMemo(() => {
    if (classes.length === 0) {
      return [];
    }
    return classes.map((item) => ({
      ...item,
      color: pickColor(item.id)
    }));
  }, [classes]);

  return (
    <main>
      <h1>YOLO Viewer</h1>
      <p className="description">快速浏览 YOLO 数据集的标注并验证框位置。</p>

      <section className="panel">
        <h2>数据选择</h2>
        <div className="select-row">
          <label htmlFor="image-select">图片</label>
          <select
            id="image-select"
            className="image-select"
            value={selectedImage}
            onChange={(event) => {
              setError(null);
              setSelectedImage(event.target.value);
            }}
          >
            <option value="" disabled>
              {images.length === 0 ? "暂无图片" : "请选择图片"}
            </option>
            {images.map((image) => (
              <option key={image.id} value={image.id}>
                {image.filename}
              </option>
            ))}
          </select>
          {loading && <span className="loading">正在加载标注...</span>}
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="panel">
        <h2>标注预览</h2>
        {selectedImage ? (
          <div className="viewer-wrapper">
            <img
              key={selectedImage}
              ref={imageRef}
              src={imageSrc}
              alt={selectedImage}
              onLoad={(event) => {
                setImageDimensions({
                  width: event.currentTarget.clientWidth,
                  height: event.currentTarget.clientHeight
                });
              }}
              onError={() => setImageError("图片加载失败")}
            />
            <div className="box-layer">
              {overlays.map((overlay) => (
                <div
                  key={overlay.id}
                  className="box"
                  style={{
                    left: `${overlay.style.left}px`,
                    top: `${overlay.style.top}px`,
                    width: `${overlay.style.width}px`,
                    height: `${overlay.style.height}px`,
                    borderColor: overlay.style.borderColor,
                    color: overlay.style.color
                  }}
                >
                  <span className="label">
                    <span
                      className="legend-color"
                      style={{ backgroundColor: overlay.color }}
                    />
                    {overlay.className}
                  </span>
                  {overlay.confidence && <span className="badge">{overlay.confidence}</span>}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="empty-state">尚未找到可视化的图片。</div>
        )}
        {imageError && <p className="error">{imageError}</p>}
      </section>

      <section className="panel">
        <h2>类别图例</h2>
        {legend.length > 0 ? (
          <div className="legend">
            {legend.map((item) => (
              <div key={item.id} className="legend-item">
                <span className="legend-color" style={{ backgroundColor: item.color }} />
                <span>{item.name}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">暂无类别信息。</p>
        )}
      </section>
    </main>
  );
}

export default App;
