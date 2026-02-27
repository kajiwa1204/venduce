"use client";

import { Header } from "@/components/header";
import { UserRanking } from "@/components/user-ranking";
import { TrendingProducts } from "@/components/trending-products";
import { LikedProducts } from "@/components/liked-products";
import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import useEmblaCarousel from "embla-carousel-react";

export default function RootPage() {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true });
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    if (!emblaApi) return;

    const onSelect = () => {
      setSelectedIndex(emblaApi.selectedScrollSnap());
    };

    emblaApi.on("select", onSelect);
    return () => {
      emblaApi.off("select", onSelect);
    };
  }, [emblaApi]);

  const slides = [
    {
      title: "ユーザーランキング",
      component: <UserRanking />,
    },
    {
      title: "売れている商品",
      component: <TrendingProducts />,
    },
    {
      title: "いいねが多い商品",
      component: <LikedProducts />,
    },
  ];

  const handlePrev = () => {
    if (emblaApi) emblaApi.scrollPrev();
  };

  const handleNext = () => {
    if (emblaApi) emblaApi.scrollNext();
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* デスクトップ: 3列グリッド */}
        <div className="hidden md:grid gap-6 lg:grid-cols-3">
          {slides.map((slide, index) => (
            <section key={index}>
              <h2 className="text-2xl font-bold mb-4 text-primary">
                {slide.title}
              </h2>
              {slide.component}
            </section>
          ))}
        </div>

        {/* モバイル: カルーセル */}
        <div className="md:hidden">
          <div className="relative">
            <div className="overflow-hidden" ref={emblaRef}>
              <div className="flex">
                {slides.map((slide, index) => (
                  <div key={index} className="min-w-full flex-shrink-0">
                    <section className="px-4">
                      <h2 className="text-2xl font-bold mb-4 text-primary">
                        {slide.title}
                      </h2>
                      {slide.component}
                    </section>
                  </div>
                ))}
              </div>
            </div>

            {/* ナビゲーション: 前後ボタン */}
            <div className="flex gap-2 justify-center mt-6">
              <Button
                variant="outline"
                size="icon"
                onClick={handlePrev}
                className="h-10 w-10 rounded-full"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={handleNext}
                className="h-10 w-10 rounded-full"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* ドットナビゲーション */}
            <div className="flex justify-center gap-2 mt-4">
              {slides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => emblaApi?.scrollTo(index)}
                  className={`h-2 w-2 rounded-full transition-colors ${
                    index === selectedIndex ? "bg-primary" : "bg-muted"
                  }`}
                  aria-label={`スライド ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
