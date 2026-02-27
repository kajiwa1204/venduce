"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Search, User, Menu, X, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import Image from "next/image";
import { useAuthStore } from "@/stores/auth";
import { useEffect, useState } from "react";
import { usersApi } from "@/lib/api/users";
import { getImageUrl } from "@/lib/utils";
import { useIsMobile } from "@/hooks/use-mobile";

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuthStore();
  const [profile, setProfile] = useState<{
    username: string;
    avatar_url?: string | null;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const isMobile = useIsMobile();

  useEffect(() => {
    if (isAuthenticated) {
      const loadProfile = async () => {
        try {
          setLoading(true);
          const userProfile = await usersApi.getProfile();
          setProfile({
            username: userProfile.username,
            avatar_url: userProfile.avatar_url,
          });
        } catch (err) {
          console.error("Failed to load profile", err);
        } finally {
          setLoading(false);
        }
      };
      loadProfile();
    }
  }, [isAuthenticated]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchQuery("");
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
    setMobileMenuOpen(false);
  };

  const navItems = [
    { label: "投稿一覧", href: "/feed" },
    { label: "商品一覧", href: "/products" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* ロゴ */}
          <Link href="/" className="flex items-center gap-2 flex-shrink-0">
            <Image
              src="/title.webp"
              alt="Venduce Title"
              width={110}
              height={341}
              className="rounded-lg h-auto w-28 sm:w-auto"
            />
          </Link>

          {/* デスクトップナビゲーション */}
          <nav className="hidden md:flex items-center gap-4 lg:gap-6 flex-1 mx-4 lg:mx-8">
            {isAuthenticated && (
              <>
                <Link
                  href="/create"
                  className="text-xs sm:text-sm font-medium text-foreground hover:text-primary transition-colors"
                >
                  投稿する
                </Link>
                <Link
                  href="/purchases"
                  className="text-xs sm:text-sm font-medium text-foreground hover:text-primary transition-colors"
                >
                  購入履歴
                </Link>
              </>
            )}
            <Link
              href="/feed"
              className="text-xs sm:text-sm font-medium text-foreground hover:text-primary transition-colors"
            >
              投稿一覧
            </Link>
            <Link
              href="/products"
              className="text-xs sm:text-sm font-medium text-foreground hover:text-primary transition-colors"
            >
              商品一覧
            </Link>
          </nav>

          {/* デスクトップ検索・プロフィール */}
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="hidden sm:flex items-center">
              <form onSubmit={handleSearch} className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="検索"
                  className="pl-9 w-40 sm:w-48 lg:w-64 transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </form>
            </div>

            {/* デスクトップ: プロフィール・設定 */}
            <div className="hidden md:flex items-center gap-2 lg:gap-4">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/profile"
                    className="flex items-center gap-2 hover:opacity-80 transition-opacity"
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarImage
                        src={getImageUrl(profile?.avatar_url ?? undefined)}
                      />
                      <AvatarFallback>
                        {profile?.username?.[0] ?? "U"}
                      </AvatarFallback>
                    </Avatar>
                    <span className="hidden lg:inline text-sm font-medium text-foreground">
                      {profile?.username}
                    </span>
                  </Link>

                  <Link href="/settings" title="設定">
                    <button className="p-2 hover:bg-muted rounded-lg transition">
                      <Settings className="h-5 w-5" />
                    </button>
                  </Link>
                </>
              ) : (
                <Link href="/login">
                  <Button
                    variant="default"
                    size="sm"
                    className="text-xs sm:text-sm"
                  >
                    ログイン
                  </Button>
                </Link>
              )}
            </div>

            {/* モバイル: ハンバーガーメニュー */}
            <div className="md:hidden">
              <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-9 w-9">
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">メニュー</span>
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-2.5/4 p-0">
                  <SheetHeader className="px-4 py-4 border-b">
                    <SheetTitle>メニュー</SheetTitle>
                  </SheetHeader>

                  <div className="flex flex-col h-full overflow-hidden">
                    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
                      {/* モバイル検索 */}
                      <form onSubmit={handleSearch}>
                        <div className="relative">
                          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input
                            type="search"
                            placeholder="検索"
                            className="pl-9 w-full text-sm"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                          />
                        </div>
                      </form>

                      {/* プロフィール情報（認証時） */}
                      {isAuthenticated && profile && (
                        <div className="flex items-center gap-3 pb-4 border-b">
                          <Avatar className="h-10 w-10">
                            <AvatarImage
                              src={getImageUrl(profile.avatar_url ?? undefined)}
                            />
                            <AvatarFallback>
                              {profile.username?.[0] ?? "U"}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-sm font-medium">
                              {profile.username}
                            </p>
                            <Link
                              href="/profile"
                              className="text-xs text-primary hover:underline"
                              onClick={() => setMobileMenuOpen(false)}
                            >
                              プロフィールを見る
                            </Link>
                          </div>
                        </div>
                      )}

                      {/* メニュー項目 */}
                      <nav className="space-y-1">
                        {isAuthenticated && (
                          <>
                            <Link
                              href="/create"
                              onClick={() => setMobileMenuOpen(false)}
                              className="block px-4 py-2.5 rounded-lg hover:bg-muted transition text-sm font-medium"
                            >
                              投稿する
                            </Link>
                            <Link
                              href="/purchases"
                              onClick={() => setMobileMenuOpen(false)}
                              className="block px-4 py-2.5 rounded-lg hover:bg-muted transition text-sm font-medium"
                            >
                              購入履歴
                            </Link>
                          </>
                        )}
                        {navItems.map((item) => (
                          <Link
                            key={item.href}
                            href={item.href}
                            onClick={() => setMobileMenuOpen(false)}
                            className="block px-4 py-2.5 rounded-lg hover:bg-muted transition text-sm font-medium"
                          >
                            {item.label}
                          </Link>
                        ))}
                      </nav>
                    </div>

                    {/* 設定・ログアウト（下部固定） */}
                    <div className="border-t space-y-2 px-4 py-4">
                      {isAuthenticated ? (
                        <>
                          <Link
                            href="/settings"
                            onClick={() => setMobileMenuOpen(false)}
                            className="flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-muted transition text-sm font-medium"
                          >
                            <Settings className="h-4 w-4" />
                            設定
                          </Link>
                          <button
                            onClick={handleLogout}
                            className="w-full text-left px-4 py-2.5 rounded-lg hover:bg-destructive/10 transition text-sm font-medium text-destructive"
                          >
                            ログアウト
                          </button>
                        </>
                      ) : (
                        <Link
                          href="/login"
                          onClick={() => setMobileMenuOpen(false)}
                          className="block w-full"
                        >
                          <Button className="w-full text-sm">ログイン</Button>
                        </Link>
                      )}
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
