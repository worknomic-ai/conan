import pytest
from conan.api.output import ConanOutput
from conans.errors import ConanException

def test_warning_as_error():
    out = ConanOutput()
    
    # Reset tags
    ConanOutput.define_silence_warnings([])
    ConanOutput.define_warnings_as_errors([])
    
    # Normal warning
    out.warning("this is a warning", warn_tag="tag1")
    
    # Promote tag1 to error
    ConanOutput.define_warnings_as_errors(["tag1"])
    with pytest.raises(ConanException) as excinfo:
        out.warning("this is an error", warn_tag="tag1")
    assert "tag1: this is an error" in str(excinfo.value)
    
    # tag2 is still a warning
    out.warning("this is just a warning", warn_tag="tag2")
    
    # Wildcard promote all to error
    ConanOutput.define_warnings_as_errors(["*"])
    with pytest.raises(ConanException) as excinfo:
        out.warning("this is an error too", warn_tag="tag2")
    assert "tag2: this is an error too" in str(excinfo.value)
    
    # Silenced warnings do NOT raise errors even if promoted
    ConanOutput.define_silence_warnings(["tag3"])
    out.warning("this is silenced", warn_tag="tag3")
    
    # Untagged warnings do NOT raise errors even if wildcard is present
    out.warning("untagged warning")

if __name__ == "__main__":
    pytest.main([__file__])
