import httpx


class BaseMethod:
    async def _get(self, method: str, **params) -> httpx.Request:
        async with httpx.AsyncClient() as client:
            params = {**params, **{"access_token": self.access_token, "v": self.api_version}}

            return await client.get(
                f"https://api.vk.com/method/{method}",
                params=params,
                headers={
                    "User-Agent": 'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)'
                }
            )

    async def get_old(self, *args, **kwargs) -> httpx.Request:
        async with httpx.AsyncClient() as client:
            return await client.get(*args, **kwargs, headers={"User-Agent": 'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)'})
