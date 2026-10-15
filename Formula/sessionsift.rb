# Unsigned, unnotarized 2.1.0 build (macOS Intel and Linux amd64). SHA-256 checks archive integrity, not publisher identity.
class Sessionsift < Formula
  desc "Local, read-only analysis of AI coding sessions"
  homepage "https://github.com/LanceSandino/sessionsift"
  version "2.1.0"
  license "PolyForm-Noncommercial-1.0.0"
  depends_on arch: :x86_64

  on_macos do
    on_intel do
      url "https://github.com/LanceSandino/sessionsift/releases/download/v2.1.0/sessionsift-2.1.0-rc13-public-darwin-amd64.tar.gz"
      sha256 "4d2c6a4b6a617fd5f046872780ef64e522c3da6ed2bdec5dd837ddf880bee234"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/LanceSandino/sessionsift/releases/download/v2.1.0/sessionsift-2.1.0-rc13-public-linux-amd64.tar.gz"
      sha256 "39d65fd70f4f02317457af9a531665d5088f307fd103d33896bc6428d3f68712"
    end
  end

  def install
    bin.install "sessionsift"
    doc.install "NOTICE", "README.md", "SECURITY.md"
    doc.install "sessionsift-2.1.0-rc13-public.spdx.json"
    pkgshare.install "LICENSE"
  end

  service do
    run [opt_bin/"sessionsift", "start"]
    keep_alive true
    require_root false
    environment_variables HOME: Dir.home
    working_dir Dir.home
  end

  test do
    ENV["HOME"] = testpath.to_s
    ENV["SESSIONSIFT_HOME"] = (testpath/"state").to_s
    ENV["CODEX_HOME"] = (testpath/"empty-codex").to_s
    ENV["CLAUDE_HOME"] = (testpath/"empty-claude").to_s
    assert_equal "2.1.0", shell_output("#{bin}/sessionsift version").strip
    assert_match "Codex", shell_output("#{bin}/sessionsift doctor")
    assert_match "sessionsift", shell_output("#{bin}/sessionsift setup mcp")
    assert_predicate doc/"NOTICE", :file?
    assert_predicate pkgshare/"LICENSE", :file?
  end
end
